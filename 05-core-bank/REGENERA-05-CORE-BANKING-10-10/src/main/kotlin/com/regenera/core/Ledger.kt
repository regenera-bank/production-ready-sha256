package com.regenera.core

import java.time.Instant
import java.time.LocalDate
import java.util.UUID

enum class PostingSide {
    DEBIT,
    CREDIT,
}

data class Posting(
    val accountId: UUID,
    val side: PostingSide,
    val amount: Money,
)

data class JournalEntry(
    val id: UUID,
    val idempotencyKey: String,
    val businessEvent: String,
    val description: String,
    val accountingDate: LocalDate,
    val occurredAt: Instant,
    val postings: List<Posting>,
    val reversalOf: UUID?,
    val immutableHash: String,
)

data class PostJournalCommand(
    val id: UUID,
    val idempotencyKey: String,
    val businessEvent: String,
    val description: String,
    val accountingDate: LocalDate,
    val occurredAt: Instant,
    val postings: List<Posting>,
    val reversalOf: UUID? = null,
)

class Ledger(private val accounts: AccountRegistry) {
    private data class AppliedRequest(
        val fingerprint: String,
        val entryId: UUID,
    )

    private val entries = linkedMapOf<UUID, JournalEntry>()
    private val requests = linkedMapOf<String, AppliedRequest>()
    private val reversalByOriginal = linkedMapOf<UUID, UUID>()

    @Synchronized
    fun post(command: PostJournalCommand): JournalEntry {
        val fingerprint = fingerprint(command)
        val existing = requests[command.idempotencyKey]
        if (existing != null) {
            if (existing.fingerprint != fingerprint) {
                throw ConflictException(
                    "LEDGER_IDEMPOTENCY_CONFLICT",
                    "A chave já foi usada para outro lançamento",
                )
            }
            return entry(existing.entryId)
        }

        validate(command)
        if (entries.containsKey(command.id)) {
            throw ConflictException(
                "LEDGER_ENTRY_ALREADY_EXISTS",
                "Identificador de lançamento já existe",
            )
        }
        if (command.reversalOf != null && reversalByOriginal.containsKey(command.reversalOf)) {
            throw ConflictException(
                "LEDGER_ALREADY_REVERSED",
                "O lançamento já possui reversão",
            )
        }

        val immutableHash = sha256(
            canonical(
                listOf(
                    command.id,
                    command.idempotencyKey,
                    command.businessEvent,
                    command.description,
                    command.accountingDate,
                    command.occurredAt,
                    command.reversalOf,
                    command.postings.map {
                        listOf(
                            it.accountId,
                            it.side,
                            it.amount.minorUnits,
                            it.amount.currency.code,
                        )
                    },
                ),
            ),
        )
        val entry = JournalEntry(
            id = command.id,
            idempotencyKey = command.idempotencyKey,
            businessEvent = command.businessEvent,
            description = command.description.trim(),
            accountingDate = command.accountingDate,
            occurredAt = command.occurredAt,
            postings = command.postings.toList(),
            reversalOf = command.reversalOf,
            immutableHash = immutableHash,
        )
        entries[entry.id] = entry
        requests[entry.idempotencyKey] = AppliedRequest(fingerprint, entry.id)
        if (entry.reversalOf != null) {
            reversalByOriginal[entry.reversalOf] = entry.id
        }
        return entry
    }

    @Synchronized
    fun reverse(
        originalEntryId: UUID,
        reversalEntryId: UUID,
        idempotencyKey: String,
        reason: String,
        accountingDate: LocalDate,
        occurredAt: Instant,
    ): JournalEntry {
        val original = entry(originalEntryId)
        val cleanReason = reason.trim()
        if (cleanReason.isEmpty() || cleanReason.length > 500) {
            throw ValidationException(
                "LEDGER_REVERSAL_REASON_INVALID",
                "Motivo da reversão é obrigatório e limitado a 500 caracteres",
            )
        }
        if (original.reversalOf != null) {
            throw StateTransitionException(
                "LEDGER_REVERSAL_OF_REVERSAL_FORBIDDEN",
                "Reversão de reversão exige novo evento de negócio",
            )
        }

        return post(
            PostJournalCommand(
                id = reversalEntryId,
                idempotencyKey = idempotencyKey,
                businessEvent = "LEDGER_ENTRY_REVERSED",
                description = "REVERSAL:${original.id}:$cleanReason",
                accountingDate = accountingDate,
                occurredAt = occurredAt,
                postings = original.postings.map {
                    it.copy(
                        side = if (it.side == PostingSide.DEBIT) {
                            PostingSide.CREDIT
                        } else {
                            PostingSide.DEBIT
                        },
                    )
                },
                reversalOf = original.id,
            ),
        )
    }

    @Synchronized
    fun entry(id: UUID): JournalEntry =
        entries[id] ?: throw NotFoundException(
            "LEDGER_ENTRY_NOT_FOUND",
            "Lançamento não encontrado: $id",
        )

    @Synchronized
    fun entries(): List<JournalEntry> = entries.values.toList()

    @Synchronized
    fun signedBalance(accountId: UUID): Money {
        val account = accounts.get(accountId)
        var balance = 0L
        for (entry in entries.values) {
            for (posting in entry.postings.filter { it.accountId == accountId }) {
                balance = Math.addExact(
                    balance,
                    signedAmount(account.accountClass, posting),
                )
            }
        }
        return Money.ofMinorUnits(balance, account.currency)
    }

    @Synchronized
    fun verifyEntryHash(id: UUID): Boolean {
        val entry = entry(id)
        val computed = sha256(
            canonical(
                listOf(
                    entry.id,
                    entry.idempotencyKey,
                    entry.businessEvent,
                    entry.description,
                    entry.accountingDate,
                    entry.occurredAt,
                    entry.reversalOf,
                    entry.postings.map {
                        listOf(
                            it.accountId,
                            it.side,
                            it.amount.minorUnits,
                            it.amount.currency.code,
                        )
                    },
                ),
            ),
        )
        return computed == entry.immutableHash
    }

    private fun validate(command: PostJournalCommand) {
        if (command.idempotencyKey.length !in 16..128) {
            throw ValidationException(
                "LEDGER_IDEMPOTENCY_KEY_INVALID",
                "Chave de idempotência inválida",
            )
        }
        if (!command.businessEvent.matches(Regex("^[A-Z][A-Z0-9_]{2,79}$"))) {
            throw ValidationException(
                "LEDGER_EVENT_INVALID",
                "Evento de negócio inválido",
            )
        }
        if (command.description.isBlank() || command.description.length > 200) {
            throw ValidationException(
                "LEDGER_DESCRIPTION_INVALID",
                "Descrição obrigatória e limitada a 200 caracteres",
            )
        }
        if (command.postings.size < 2 || command.postings.size > 200) {
            throw ValidationException(
                "LEDGER_POSTING_COUNT_INVALID",
                "Lançamento precisa ter entre 2 e 200 linhas",
            )
        }

        val currencies = command.postings.map { it.amount.currency }.distinct()
        if (currencies.size != 1) {
            throw ValidationException(
                "LEDGER_MIXED_CURRENCY",
                "Um lançamento não mistura moedas",
            )
        }

        var debit = 0L
        var credit = 0L
        for (posting in command.postings) {
            val account = accounts.requireOpen(posting.accountId)
            if (account.currency != posting.amount.currency) {
                throw ValidationException(
                    "LEDGER_ACCOUNT_CURRENCY_MISMATCH",
                    "Moeda da linha não corresponde à conta",
                )
            }
            if (!posting.amount.isPositive()) {
                throw ValidationException(
                    "LEDGER_AMOUNT_NOT_POSITIVE",
                    "Linha contábil exige valor positivo",
                )
            }
            if (posting.side == PostingSide.DEBIT) {
                debit = Math.addExact(debit, posting.amount.minorUnits)
            } else {
                credit = Math.addExact(credit, posting.amount.minorUnits)
            }
        }
        if (debit != credit) {
            throw ValidationException(
                "LEDGER_UNBALANCED",
                "Débitos e créditos não fecham",
            )
        }

        if (command.reversalOf != null) {
            entry(command.reversalOf)
        }
    }

    private fun fingerprint(command: PostJournalCommand): String = sha256(
        canonical(
            listOf(
                command.businessEvent,
                command.description.trim(),
                command.accountingDate,
                command.reversalOf,
                command.postings.map {
                    listOf(
                        it.accountId,
                        it.side,
                        it.amount.minorUnits,
                        it.amount.currency.code,
                    )
                },
            ),
        ),
    )

    private fun signedAmount(accountClass: AccountClass, posting: Posting): Long {
        val normalDebit = accountClass == AccountClass.ASSET ||
            accountClass == AccountClass.EXPENSE
        return when {
            normalDebit && posting.side == PostingSide.DEBIT -> posting.amount.minorUnits
            normalDebit && posting.side == PostingSide.CREDIT -> -posting.amount.minorUnits
            !normalDebit && posting.side == PostingSide.CREDIT -> posting.amount.minorUnits
            else -> -posting.amount.minorUnits
        }
    }
}
