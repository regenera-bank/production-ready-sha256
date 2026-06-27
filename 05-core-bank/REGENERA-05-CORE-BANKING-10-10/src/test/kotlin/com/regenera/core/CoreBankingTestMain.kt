package com.regenera.core

import java.security.SecureRandom
import java.time.Instant
import java.time.LocalDate
import java.time.temporal.ChronoUnit
import java.util.UUID
import java.util.concurrent.Callable
import java.util.concurrent.Executors

private object TestSuite {
    private var passed = 0
    private var failed = 0

    fun test(name: String, block: () -> Unit) {
        try {
            block()
            println("PASS $name")
            passed += 1
        } catch (error: Throwable) {
            println("FAIL $name :: ${error::class.simpleName} :: ${error.message}")
            failed += 1
        }
    }

    fun finish() {
        println("SUMMARY passed=$passed failed=$failed total=${passed + failed}")
        if (failed > 0) throw IllegalStateException("$failed teste(s) falharam")
    }
}

private inline fun <reified T : Throwable> expectThrows(block: () -> Unit): T {
    try {
        block()
    } catch (error: Throwable) {
        if (error is T) return error
        throw AssertionError("Esperava ${T::class.simpleName}, recebeu ${error::class.simpleName}")
    }
    throw AssertionError("Esperava ${T::class.simpleName}, mas nada foi lançado")
}

private fun uuid(value: String): UUID = UUID.fromString(value)

private val owner = uuid("00000000-0000-4000-8000-000000000001")
private val cash = uuid("00000000-0000-4000-8000-000000000010")
private val customer = uuid("00000000-0000-4000-8000-000000000011")
private val clearing = uuid("00000000-0000-4000-8000-000000000012")
private val instant = Instant.parse("2026-06-26T12:00:00Z")

private fun fundedCore(amount: Long = 100_000L): CoreBank {
    val core = CoreBank()
    core.accounts.open(cash, owner, AccountClass.ASSET, Currency.BRL)
    core.accounts.open(customer, owner, AccountClass.LIABILITY, Currency.BRL)
    core.accounts.open(clearing, owner, AccountClass.LIABILITY, Currency.BRL)
    core.ledger.post(
        PostJournalCommand(
            id = uuid("10000000-0000-4000-8000-000000000001"),
            idempotencyKey = "opening-balance-0001",
            businessEvent = "OPENING_BALANCE",
            description = "Abertura controlada",
            accountingDate = LocalDate.parse("2026-06-26"),
            occurredAt = instant,
            postings = listOf(
                Posting(cash, PostingSide.DEBIT, Money.ofMinorUnits(amount)),
                Posting(customer, PostingSide.CREDIT, Money.ofMinorUnits(amount)),
            ),
        ),
    )
    return core
}

private fun paymentCommand(
    id: UUID = uuid("20000000-0000-4000-8000-000000000001"),
    key: String = "payment-key-00000001",
    amount: Long = 10_000L,
    at: Instant = instant.plusSeconds(10),
): CreatePaymentCommand = CreatePaymentCommand(
    paymentId = id,
    senderAccountId = customer,
    clearingAccountId = clearing,
    amount = Money.ofMinorUnits(amount),
    idempotencyKey = key,
    correlationId = uuid("30000000-0000-4000-8000-000000000001"),
    occurredAt = at,
)

fun main() {
    TestSuite.test("currency rejects invalid code") {
        expectThrows<ValidationException> { Currency.of("REAL") }
    }

    TestSuite.test("money adds exact minor units") {
        check(Money.ofMinorUnits(120).plus(Money.ofMinorUnits(30)).minorUnits == 150L)
    }

    TestSuite.test("money rejects mixed currency") {
        expectThrows<ValidationException> {
            Money.ofMinorUnits(100, Currency.BRL)
                .plus(Money.ofMinorUnits(100, Currency.of("USD")))
        }
    }

    TestSuite.test("money rejects arithmetic overflow") {
        expectThrows<ArithmeticException> {
            Money.ofMinorUnits(Long.MAX_VALUE).plus(Money.ofMinorUnits(1))
        }
    }

    TestSuite.test("percentage rounds positive half away from zero") {
        check(Money.ofMinorUnits(1).percentageBasisPoints(5_000).minorUnits == 1L)
    }

    TestSuite.test("percentage rounds negative half away from zero") {
        check(Money.ofMinorUnits(-1).percentageBasisPoints(5_000).minorUnits == -1L)
    }

    TestSuite.test("account cannot be opened twice") {
        val registry = AccountRegistry()
        registry.open(customer, owner, AccountClass.LIABILITY, Currency.BRL)
        expectThrows<ConflictException> {
            registry.open(customer, owner, AccountClass.LIABILITY, Currency.BRL)
        }
    }

    TestSuite.test("blocked account cannot be used") {
        val core = fundedCore()
        core.accounts.block(customer)
        expectThrows<StateTransitionException> { core.accounts.requireOpen(customer) }
    }

    TestSuite.test("closed account does not reopen") {
        val registry = AccountRegistry()
        registry.open(customer, owner, AccountClass.LIABILITY, Currency.BRL)
        registry.close(customer)
        expectThrows<StateTransitionException> { registry.reopen(customer) }
    }

    TestSuite.test("ledger rejects unbalanced entry") {
        val core = fundedCore()
        expectThrows<ValidationException> {
            core.ledger.post(
                PostJournalCommand(
                    id = UUID.randomUUID(),
                    idempotencyKey = "unbalanced-entry-001",
                    businessEvent = "UNBALANCED_ATTEMPT",
                    description = "Não deve entrar",
                    accountingDate = LocalDate.parse("2026-06-26"),
                    occurredAt = instant,
                    postings = listOf(
                        Posting(customer, PostingSide.DEBIT, Money.ofMinorUnits(100)),
                        Posting(clearing, PostingSide.CREDIT, Money.ofMinorUnits(99)),
                    ),
                ),
            )
        }
    }

    TestSuite.test("ledger rejects mixed currency") {
        val core = fundedCore()
        val usd = uuid("00000000-0000-4000-8000-000000000099")
        core.accounts.open(usd, owner, AccountClass.LIABILITY, Currency.of("USD"))
        expectThrows<ValidationException> {
            core.ledger.post(
                PostJournalCommand(
                    id = UUID.randomUUID(),
                    idempotencyKey = "mixed-currency-0001",
                    businessEvent = "MIXED_CURRENCY",
                    description = "Não deve entrar",
                    accountingDate = LocalDate.parse("2026-06-26"),
                    occurredAt = instant,
                    postings = listOf(
                        Posting(customer, PostingSide.DEBIT, Money.ofMinorUnits(100)),
                        Posting(usd, PostingSide.CREDIT, Money.ofMinorUnits(100, Currency.of("USD"))),
                    ),
                ),
            )
        }
    }

    TestSuite.test("ledger rejects non positive line") {
        val core = fundedCore()
        expectThrows<ValidationException> {
            core.ledger.post(
                PostJournalCommand(
                    id = UUID.randomUUID(),
                    idempotencyKey = "zero-posting-line-01",
                    businessEvent = "ZERO_LINE",
                    description = "Não deve entrar",
                    accountingDate = LocalDate.parse("2026-06-26"),
                    occurredAt = instant,
                    postings = listOf(
                        Posting(customer, PostingSide.DEBIT, Money.zero()),
                        Posting(clearing, PostingSide.CREDIT, Money.zero()),
                    ),
                ),
            )
        }
    }

    TestSuite.test("ledger returns original result for duplicate request") {
        val core = fundedCore()
        val command = PostJournalCommand(
            id = UUID.randomUUID(),
            idempotencyKey = "ledger-duplicate-0001",
            businessEvent = "TRANSFER_POSTED",
            description = "Transferência",
            accountingDate = LocalDate.parse("2026-06-26"),
            occurredAt = instant,
            postings = listOf(
                Posting(customer, PostingSide.DEBIT, Money.ofMinorUnits(100)),
                Posting(clearing, PostingSide.CREDIT, Money.ofMinorUnits(100)),
            ),
        )
        val first = core.ledger.post(command)
        val replay = core.ledger.post(command.copy(id = UUID.randomUUID()))
        check(first.id == replay.id)
        check(core.ledger.entries().size == 2)
    }

    TestSuite.test("ledger rejects duplicate key with different payload") {
        val core = fundedCore()
        val base = PostJournalCommand(
            id = UUID.randomUUID(),
            idempotencyKey = "ledger-conflict-0001",
            businessEvent = "TRANSFER_POSTED",
            description = "Transferência",
            accountingDate = LocalDate.parse("2026-06-26"),
            occurredAt = instant,
            postings = listOf(
                Posting(customer, PostingSide.DEBIT, Money.ofMinorUnits(100)),
                Posting(clearing, PostingSide.CREDIT, Money.ofMinorUnits(100)),
            ),
        )
        core.ledger.post(base)
        expectThrows<ConflictException> {
            core.ledger.post(
                base.copy(
                    id = UUID.randomUUID(),
                    postings = listOf(
                        Posting(customer, PostingSide.DEBIT, Money.ofMinorUnits(101)),
                        Posting(clearing, PostingSide.CREDIT, Money.ofMinorUnits(101)),
                    ),
                ),
            )
        }
    }

    TestSuite.test("ledger entry hash remains valid") {
        val core = fundedCore()
        check(core.ledger.verifyEntryHash(uuid("10000000-0000-4000-8000-000000000001")))
    }

    TestSuite.test("reversal creates compensating entry") {
        val core = fundedCore()
        val original = core.ledger.post(
            PostJournalCommand(
                id = uuid("10000000-0000-4000-8000-000000000002"),
                idempotencyKey = "ledger-reversal-base-01",
                businessEvent = "PAYMENT_DEBITED",
                description = "Pagamento",
                accountingDate = LocalDate.parse("2026-06-26"),
                occurredAt = instant,
                postings = listOf(
                    Posting(customer, PostingSide.DEBIT, Money.ofMinorUnits(500)),
                    Posting(clearing, PostingSide.CREDIT, Money.ofMinorUnits(500)),
                ),
            ),
        )
        val reversal = core.ledger.reverse(
            original.id,
            uuid("10000000-0000-4000-8000-000000000003"),
            "ledger-reversal-0001",
            "Provedor rejeitou",
            LocalDate.parse("2026-06-26"),
            instant.plusSeconds(1),
        )
        check(reversal.reversalOf == original.id)
        check(reversal.postings[0].side == PostingSide.CREDIT)
        check(core.ledger.signedBalance(customer).minorUnits == 100_000L)
    }

    TestSuite.test("second reversal is rejected") {
        val core = fundedCore()
        val original = core.ledger.post(
            PostJournalCommand(
                id = UUID.randomUUID(),
                idempotencyKey = "ledger-second-rev-base",
                businessEvent = "PAYMENT_DEBITED",
                description = "Pagamento",
                accountingDate = LocalDate.parse("2026-06-26"),
                occurredAt = instant,
                postings = listOf(
                    Posting(customer, PostingSide.DEBIT, Money.ofMinorUnits(500)),
                    Posting(clearing, PostingSide.CREDIT, Money.ofMinorUnits(500)),
                ),
            ),
        )
        core.ledger.reverse(
            original.id,
            UUID.randomUUID(),
            "ledger-second-rev-001",
            "Primeira reversão",
            LocalDate.parse("2026-06-26"),
            instant.plusSeconds(1),
        )
        expectThrows<ConflictException> {
            core.ledger.reverse(
                original.id,
                UUID.randomUUID(),
                "ledger-second-rev-002",
                "Segunda reversão",
                LocalDate.parse("2026-06-26"),
                instant.plusSeconds(2),
            )
        }
    }

    TestSuite.test("liability balance follows accounting side") {
        val core = fundedCore()
        check(core.ledger.signedBalance(customer).minorUnits == 100_000L)
        check(core.ledger.signedBalance(cash).minorUnits == 100_000L)
    }

    TestSuite.test("idempotency completes and replays") {
        val registry = IdempotencyRegistry()
        val hash = "a".repeat(64)
        check(registry.begin("payment:create", "idempotency-key-0001", hash, instant) is IdempotencyBegin.Acquired)
        registry.complete("payment:create", "idempotency-key-0001", "response-1", instant)
        val replay = registry.begin("payment:create", "idempotency-key-0001", hash, instant)
        check(replay == IdempotencyBegin.Replay("response-1"))
    }

    TestSuite.test("idempotency unknown blocks execution") {
        val registry = IdempotencyRegistry()
        val hash = "b".repeat(64)
        registry.begin("payment:create", "idempotency-key-0002", hash, instant)
        registry.markUnknown("payment:create", "idempotency-key-0002", instant)
        val blocked = registry.begin("payment:create", "idempotency-key-0002", hash, instant)
        check(blocked == IdempotencyBegin.Blocked(IdempotencyState.UNKNOWN))
    }

    TestSuite.test("idempotency retryable can be reacquired") {
        val registry = IdempotencyRegistry()
        val hash = "c".repeat(64)
        registry.begin("payment:create", "idempotency-key-0003", hash, instant)
        registry.failRetryable("payment:create", "idempotency-key-0003", instant)
        check(registry.begin("payment:create", "idempotency-key-0003", hash, instant) is IdempotencyBegin.Acquired)
    }

    TestSuite.test("idempotency rejects payload drift") {
        val registry = IdempotencyRegistry()
        registry.begin("payment:create", "idempotency-key-0004", "d".repeat(64), instant)
        expectThrows<ConflictException> {
            registry.begin("payment:create", "idempotency-key-0004", "e".repeat(64), instant)
        }
    }

    TestSuite.test("hold reduces available balance") {
        val core = fundedCore()
        core.holds.place(
            UUID.randomUUID(),
            customer,
            Money.ofMinorUnits(20_000),
            "Compra autorizada",
            instant,
            instant.plus(1, ChronoUnit.HOURS),
        )
        check(core.holds.availableBalance(customer, instant).minorUnits == 80_000L)
    }

    TestSuite.test("hold cannot exceed available balance") {
        val core = fundedCore()
        expectThrows<ConflictException> {
            core.holds.place(
                UUID.randomUUID(),
                customer,
                Money.ofMinorUnits(100_001),
                "Compra",
                instant,
                instant.plusSeconds(60),
            )
        }
    }

    TestSuite.test("released hold restores available balance") {
        val core = fundedCore()
        val hold = core.holds.place(
            UUID.randomUUID(),
            customer,
            Money.ofMinorUnits(10_000),
            "Compra",
            instant,
            instant.plusSeconds(60),
        )
        core.holds.release(hold.id, instant.plusSeconds(1))
        check(core.holds.availableBalance(customer, instant.plusSeconds(2)).minorUnits == 100_000L)
    }

    TestSuite.test("expired hold stops reserving funds") {
        val core = fundedCore()
        val hold = core.holds.place(
            UUID.randomUUID(),
            customer,
            Money.ofMinorUnits(10_000),
            "Compra",
            instant,
            instant.plusSeconds(1),
        )
        core.holds.expire(instant.plusSeconds(2))
        check(core.holds.get(hold.id).status == HoldStatus.EXPIRED)
        check(core.holds.availableBalance(customer, instant.plusSeconds(2)).minorUnits == 100_000L)
    }

    TestSuite.test("payment debit is atomic across ledger outbox and audit") {
        val core = fundedCore()
        val payment = core.payments.create(paymentCommand())
        check(payment.status == PaymentStatus.DEBITED)
        check(core.ledger.signedBalance(customer).minorUnits == 90_000L)
        check(core.outbox.pending(10).size == 1)
        check(core.audit.events().size == 1)
        check(core.audit.verify())
    }

    TestSuite.test("payment duplicate returns original result") {
        val core = fundedCore()
        val command = paymentCommand()
        val first = core.payments.create(command)
        val replay = core.payments.create(command)
        check(first == replay)
        check(core.payments.all().size == 1)
        check(core.ledger.entries().size == 2)
    }

    TestSuite.test("payment payload drift is rejected") {
        val core = fundedCore()
        val command = paymentCommand()
        core.payments.create(command)
        expectThrows<ConflictException> {
            core.payments.create(command.copy(amount = Money.ofMinorUnits(10_001)))
        }
    }

    TestSuite.test("payment rejects insufficient funds") {
        val core = fundedCore()
        expectThrows<ConflictException> {
            core.payments.create(paymentCommand(amount = 100_001))
        }
    }

    TestSuite.test("payment follows sent and settled states") {
        val core = fundedCore()
        val payment = core.payments.create(paymentCommand())
        check(core.payments.markSent(payment.id, instant.plusSeconds(20)).status == PaymentStatus.SENT)
        check(core.payments.markSettled(payment.id, instant.plusSeconds(30)).status == PaymentStatus.SETTLED)
    }

    TestSuite.test("payment rejects invalid transition") {
        val core = fundedCore()
        val payment = core.payments.create(paymentCommand())
        expectThrows<StateTransitionException> {
            core.payments.markSettled(payment.id, instant.plusSeconds(20))
        }
    }

    TestSuite.test("unknown payment cannot be retried blindly") {
        val core = fundedCore()
        val payment = core.payments.create(paymentCommand())
        core.payments.markUnknown(payment.id, instant.plusSeconds(20))
        expectThrows<StateTransitionException> { core.payments.requestRetry(payment.id) }
    }

    TestSuite.test("unknown payment can reconcile to settled") {
        val core = fundedCore()
        val payment = core.payments.create(paymentCommand())
        core.payments.markUnknown(payment.id, instant.plusSeconds(20))
        core.payments.openReconciliation(payment.id, instant.plusSeconds(21))
        val settled = core.payments.reconcile(
            payment.id,
            ExternalOutcome.SETTLED,
            null,
            instant.plusSeconds(30),
        )
        check(settled.status == PaymentStatus.SETTLED)
        check(core.ledger.signedBalance(customer).minorUnits == 90_000L)
    }

    TestSuite.test("rejected reconciliation creates compensating entry") {
        val core = fundedCore()
        val payment = core.payments.create(paymentCommand())
        core.payments.markUnknown(payment.id, instant.plusSeconds(20))
        core.payments.openReconciliation(payment.id, instant.plusSeconds(21))
        val reversed = core.payments.reconcile(
            payment.id,
            ExternalOutcome.REJECTED,
            uuid("40000000-0000-4000-8000-000000000001"),
            instant.plusSeconds(30),
        )
        check(reversed.status == PaymentStatus.REVERSED)
        check(core.ledger.signedBalance(customer).minorUnits == 100_000L)
        check(core.ledger.entries().size == 3)
    }

    TestSuite.test("concurrent duplicate payment produces one financial effect") {
        val core = fundedCore()
        val command = paymentCommand()
        val pool = Executors.newFixedThreadPool(8)
        try {
            val results = pool.invokeAll(
                (1..16).map { Callable { core.payments.create(command).id } },
            ).map { it.get() }
            check(results.toSet().size == 1)
            check(core.payments.all().size == 1)
            check(core.ledger.entries().size == 2)
            check(core.ledger.signedBalance(customer).minorUnits == 90_000L)
        } finally {
            pool.shutdownNow()
        }
    }

    TestSuite.test("audit chain detects tampering") {
        val chain = AuditChain()
        chain.append("ACCOUNT_OPENED", "operator-1", "account-1", mapOf("status" to "OPEN"), instant)
        chain.append("ACCOUNT_BLOCKED", "operator-2", "account-1", mapOf("reason" to "RISK"), instant.plusSeconds(1))
        check(chain.verify())
        val tampered = chain.events().toMutableList()
        tampered[0] = tampered[0].copy(payload = mapOf("status" to "CLOSED"))
        check(!AuditChain.verify(tampered))
    }

    TestSuite.test("outbox publish is idempotent") {
        val outbox = Outbox()
        val id = UUID.randomUUID()
        outbox.append(
            OutboxEvent(
                id,
                "PAYMENT",
                UUID.randomUUID(),
                "PAYMENT_DEBITED",
                mapOf("a" to "b"),
                instant,
                null,
            ),
        )
        val first = outbox.markPublished(id, instant.plusSeconds(1))
        val second = outbox.markPublished(id, instant.plusSeconds(2))
        check(first == second)
    }

    TestSuite.test("outbox rejects invalid batch limit") {
        expectThrows<ValidationException> { Outbox().pending(0) }
    }

    TestSuite.test("pix generates canonical end to end id") {
        val core = fundedCore()
        val deterministic = object : SecureRandom() {
            override fun nextInt(bound: Int): Int = 1
        }
        val pix = PixEngine(
            core.payments,
            "12345678",
            ByteArray(32) { (it + 1).toByte() },
            deterministic,
        )
        val result = pix.create(
            paymentCommand(),
            "cliente@example.com",
            "87654321",
        )
        check(result.internalEndToEndId.matches(Regex("^E12345678[0-9]{12}[a-z0-9]{11}$")))
        check(result.internalEndToEndId.length == 32)
    }

    TestSuite.test("pix does not retain raw key") {
        val core = fundedCore()
        val pix = PixEngine(
            core.payments,
            "12345678",
            ByteArray(32) { (it + 1).toByte() },
        )
        val raw = "cliente@example.com"
        val result = pix.create(paymentCommand(), raw, null)
        check(result.receiverKeyMasked != raw)
        check(result.receiverKeyHash != raw)
        check(!result.toString().contains(raw))
    }

    TestSuite.test("pix rejects weak hmac secret") {
        val core = fundedCore()
        expectThrows<ValidationException> {
            PixEngine(core.payments, "12345678", ByteArray(8))
        }
    }

    TestSuite.test("pix rejects invalid ispb") {
        val core = fundedCore()
        expectThrows<ValidationException> {
            PixEngine(core.payments, "123", ByteArray(32))
        }
    }


    TestSuite.test("payment respects active holds") {
        val core = fundedCore()
        core.holds.place(
            UUID.randomUUID(),
            customer,
            Money.ofMinorUnits(95_000),
            "Compra autorizada",
            instant,
            instant.plusSeconds(300),
        )
        expectThrows<ConflictException> {
            core.payments.create(paymentCommand(amount = 10_000))
        }
    }

    TestSuite.test("failed payment request is not left processing") {
        val core = fundedCore()
        val command = paymentCommand(amount = 100_001, key = "payment-failure-key-01")
        expectThrows<ConflictException> { core.payments.create(command) }
        check(
            core.idempotency.get("payment:create", command.idempotencyKey)?.state ==
                IdempotencyState.FAILED_FINAL,
        )
    }

    TestSuite.test("payment rejects non liability accounting accounts") {
        val core = fundedCore()
        val assetClearing = uuid("00000000-0000-4000-8000-000000000088")
        core.accounts.open(assetClearing, owner, AccountClass.ASSET, Currency.BRL)
        expectThrows<ValidationException> {
            core.payments.create(
                paymentCommand(
                    id = uuid("20000000-0000-4000-8000-000000000088"),
                    key = "payment-asset-account-01",
                ).copy(clearingAccountId = assetClearing),
            )
        }
    }

    TestSuite.test("pix replay returns the same end to end id") {
        val core = fundedCore()
        val deterministic = object : SecureRandom() {
            private var next = 0
            override fun nextInt(bound: Int): Int = (next++ % bound)
        }
        val pix = PixEngine(
            core.payments,
            "12345678",
            ByteArray(32) { (it + 1).toByte() },
            deterministic,
        )
        val command = paymentCommand()
        val first = pix.create(command, "cliente@example.com", "87654321")
        val replay = pix.create(command, "cliente@example.com", "87654321")
        check(first == replay)
        check(core.ledger.entries().size == 2)
    }

    TestSuite.finish()
}
