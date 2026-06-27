package com.regenera.core

import java.time.Instant
import java.time.LocalDate
import java.util.UUID

enum class PaymentStatus {
    RECEIVED,
    VALIDATED,
    AUTHORIZED,
    DEBITED,
    SENT,
    SETTLED,
    FAILED,
    UNKNOWN,
    RECONCILIATION_REQUIRED,
    REVERSED,
}

data class Payment(
    val id: UUID,
    val senderAccountId: UUID,
    val clearingAccountId: UUID,
    val amount: Money,
    val status: PaymentStatus,
    val ledgerEntryId: UUID?,
    val reversalEntryId: UUID?,
    val correlationId: UUID,
    val createdAt: Instant,
    val updatedAt: Instant,
)

data class CreatePaymentCommand(
    val paymentId: UUID,
    val senderAccountId: UUID,
    val clearingAccountId: UUID,
    val amount: Money,
    val idempotencyKey: String,
    val correlationId: UUID,
    val occurredAt: Instant,
)

enum class ExternalOutcome {
    SETTLED,
    REJECTED,
}

class PaymentEngine(
    private val accounts: AccountRegistry,
    private val ledger: Ledger,
    private val idempotency: IdempotencyRegistry,
    private val holds: HoldBook,
    private val outbox: Outbox,
    private val audit: AuditChain,
) {
    private val payments = linkedMapOf<UUID, Payment>()

    @Synchronized
    fun create(command: CreatePaymentCommand): Payment {
        validate(command)
        val payloadHash = sha256(
            canonical(
                listOf(
                    command.paymentId,
                    command.senderAccountId,
                    command.clearingAccountId,
                    command.amount.minorUnits,
                    command.amount.currency.code,
                    command.correlationId,
                ),
            ),
        )
        return when (
            val begin = idempotency.begin(
                "payment:create",
                command.idempotencyKey,
                payloadHash,
                command.occurredAt,
            )
        ) {
            is IdempotencyBegin.Replay -> payment(UUID.fromString(begin.responseReference))
            is IdempotencyBegin.Blocked -> throw StateTransitionException(
                "PAYMENT_IDEMPOTENCY_BLOCKED",
                "Operação bloqueada em estado ${begin.state}",
            )
            is IdempotencyBegin.Acquired -> {
                try {
                    createNew(command)
                } catch (error: CoreBankingException) {
                    idempotency.failFinal(
                        "payment:create",
                        command.idempotencyKey,
                        command.occurredAt,
                    )
                    throw error
                } catch (error: Throwable) {
                    idempotency.failRetryable(
                        "payment:create",
                        command.idempotencyKey,
                        command.occurredAt,
                    )
                    throw error
                }
            }
        }
    }

    @Synchronized
    fun markSent(paymentId: UUID, at: Instant): Payment =
        transition(paymentId, PaymentStatus.SENT, at)

    @Synchronized
    fun markSettled(paymentId: UUID, at: Instant): Payment =
        transition(paymentId, PaymentStatus.SETTLED, at)

    @Synchronized
    fun markUnknown(paymentId: UUID, at: Instant): Payment {
        val current = payment(paymentId)
        val next = when (current.status) {
            PaymentStatus.DEBITED,
            PaymentStatus.SENT,
            -> current.copy(status = PaymentStatus.UNKNOWN, updatedAt = at)
            else -> throw StateTransitionException(
                "PAYMENT_UNKNOWN_FORBIDDEN",
                "Estado ${current.status} não pode virar UNKNOWN",
            )
        }
        payments[paymentId] = next
        audit.append(
            "PAYMENT_MARKED_UNKNOWN",
            "core-banking",
            paymentId.toString(),
            mapOf("previousStatus" to current.status.name),
            at,
        )
        return next
    }

    @Synchronized
    fun requestRetry(paymentId: UUID): Payment {
        val payment = payment(paymentId)
        if (
            payment.status == PaymentStatus.UNKNOWN ||
            payment.status == PaymentStatus.RECONCILIATION_REQUIRED
        ) {
            throw StateTransitionException(
                "PAYMENT_BLIND_RETRY_FORBIDDEN",
                "Estado desconhecido exige reconciliação",
            )
        }
        return payment
    }

    @Synchronized
    fun openReconciliation(paymentId: UUID, at: Instant): Payment {
        val current = payment(paymentId)
        if (current.status != PaymentStatus.UNKNOWN) {
            throw StateTransitionException(
                "PAYMENT_RECONCILIATION_NOT_REQUIRED",
                "Reconciliação só abre para estado UNKNOWN",
            )
        }
        val next = current.copy(
            status = PaymentStatus.RECONCILIATION_REQUIRED,
            updatedAt = at,
        )
        payments[paymentId] = next
        return next
    }

    @Synchronized
    fun reconcile(
        paymentId: UUID,
        outcome: ExternalOutcome,
        reversalEntryId: UUID?,
        at: Instant,
    ): Payment {
        val current = payment(paymentId)
        if (current.status != PaymentStatus.RECONCILIATION_REQUIRED) {
            throw StateTransitionException(
                "PAYMENT_RECONCILIATION_STATE_INVALID",
                "Pagamento não está aguardando reconciliação",
            )
        }
        val next = when (outcome) {
            ExternalOutcome.SETTLED -> current.copy(
                status = PaymentStatus.SETTLED,
                updatedAt = at,
            )
            ExternalOutcome.REJECTED -> {
                val originalEntryId = current.ledgerEntryId
                    ?: throw IllegalStateException("Pagamento debitado sem lançamento")
                val reversalId = reversalEntryId ?: throw ValidationException(
                    "PAYMENT_REVERSAL_ID_REQUIRED",
                    "Reconciliação rejeitada exige reversão",
                )
                ledger.reverse(
                    originalEntryId = originalEntryId,
                    reversalEntryId = reversalId,
                    idempotencyKey = "payment-reversal-${current.id}",
                    reason = "RECONCILIATION_REJECTED",
                    accountingDate = LocalDate.ofInstant(at, java.time.ZoneOffset.UTC),
                    occurredAt = at,
                )
                current.copy(
                    status = PaymentStatus.REVERSED,
                    reversalEntryId = reversalId,
                    updatedAt = at,
                )
            }
        }
        payments[paymentId] = next
        audit.append(
            "PAYMENT_RECONCILED",
            "core-banking",
            paymentId.toString(),
            mapOf("outcome" to outcome.name, "status" to next.status.name),
            at,
        )
        return next
    }

    @Synchronized
    fun payment(id: UUID): Payment = payments[id] ?: throw NotFoundException(
        "PAYMENT_NOT_FOUND",
        "Pagamento não encontrado: $id",
    )

    @Synchronized
    fun all(): List<Payment> = payments.values.toList()

    private fun createNew(command: CreatePaymentCommand): Payment {
        if (payments.containsKey(command.paymentId)) {
            throw ConflictException("PAYMENT_ALREADY_EXISTS", "Pagamento já existe")
        }
        val sender = accounts.requireOpen(command.senderAccountId)
        val clearing = accounts.requireOpen(command.clearingAccountId)
        if (sender.accountClass != AccountClass.LIABILITY || clearing.accountClass != AccountClass.LIABILITY) {
            throw ValidationException(
                "PAYMENT_ACCOUNT_CLASS_INVALID",
                "Pagamento exige contas contábeis de passivo",
            )
        }
        if (sender.currency != command.amount.currency || clearing.currency != command.amount.currency) {
            throw ValidationException(
                "PAYMENT_CURRENCY_MISMATCH",
                "Contas e pagamento precisam usar a mesma moeda",
            )
        }
        val available = holds.availableBalance(sender.id, command.occurredAt)
        if (available < command.amount) {
            throw ConflictException(
                "PAYMENT_INSUFFICIENT_FUNDS",
                "Saldo insuficiente",
            )
        }

        val ledgerEntryId = UUID.nameUUIDFromBytes(
            "payment-ledger:${command.paymentId}".toByteArray(),
        )
        ledger.post(
            PostJournalCommand(
                id = ledgerEntryId,
                idempotencyKey = "payment-ledger-${sha256(command.idempotencyKey).take(32)}",
                businessEvent = "PAYMENT_DEBITED",
                description = "PAYMENT:${command.paymentId}",
                accountingDate = LocalDate.ofInstant(
                    command.occurredAt,
                    java.time.ZoneOffset.UTC,
                ),
                occurredAt = command.occurredAt,
                postings = listOf(
                    Posting(sender.id, PostingSide.DEBIT, command.amount),
                    Posting(clearing.id, PostingSide.CREDIT, command.amount),
                ),
            ),
        )
        val payment = Payment(
            id = command.paymentId,
            senderAccountId = sender.id,
            clearingAccountId = clearing.id,
            amount = command.amount,
            status = PaymentStatus.DEBITED,
            ledgerEntryId = ledgerEntryId,
            reversalEntryId = null,
            correlationId = command.correlationId,
            createdAt = command.occurredAt,
            updatedAt = command.occurredAt,
        )
        payments[payment.id] = payment
        outbox.append(
            OutboxEvent(
                id = UUID.nameUUIDFromBytes(
                    "payment-outbox:${payment.id}".toByteArray(),
                ),
                aggregateType = "PAYMENT",
                aggregateId = payment.id,
                eventType = "PAYMENT_DEBITED",
                payload = mapOf(
                    "paymentId" to payment.id.toString(),
                    "amountMinorUnits" to payment.amount.minorUnits.toString(),
                    "currency" to payment.amount.currency.code,
                ),
                occurredAt = command.occurredAt,
                publishedAt = null,
            ),
        )
        audit.append(
            "PAYMENT_CREATED",
            "core-banking",
            payment.id.toString(),
            mapOf(
                "status" to payment.status.name,
                "correlationId" to command.correlationId.toString(),
            ),
            command.occurredAt,
        )
        idempotency.complete(
            "payment:create",
            command.idempotencyKey,
            payment.id.toString(),
            command.occurredAt,
        )
        return payment
    }

    private fun transition(id: UUID, target: PaymentStatus, at: Instant): Payment {
        val current = payment(id)
        val allowed = when (target) {
            PaymentStatus.SENT -> setOf(PaymentStatus.DEBITED)
            PaymentStatus.SETTLED -> setOf(PaymentStatus.SENT)
            else -> emptySet()
        }
        if (current.status !in allowed) {
            throw StateTransitionException(
                "PAYMENT_TRANSITION_FORBIDDEN",
                "Transição ${current.status} -> $target não permitida",
            )
        }
        val next = current.copy(status = target, updatedAt = at)
        payments[id] = next
        return next
    }

    private fun validate(command: CreatePaymentCommand) {
        if (!command.amount.isPositive()) {
            throw ValidationException(
                "PAYMENT_AMOUNT_NOT_POSITIVE",
                "Pagamento exige valor positivo",
            )
        }
        if (command.idempotencyKey.length !in 16..128) {
            throw ValidationException(
                "PAYMENT_IDEMPOTENCY_KEY_INVALID",
                "Chave de idempotência inválida",
            )
        }
    }
}
