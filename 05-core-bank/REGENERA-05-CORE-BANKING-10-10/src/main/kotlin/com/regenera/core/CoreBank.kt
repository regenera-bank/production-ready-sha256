package com.regenera.core

class CoreBank {
    val accounts = AccountRegistry()
    val ledger = Ledger(accounts)
    val idempotency = IdempotencyRegistry()
    val outbox = Outbox()
    val audit = AuditChain()
    val holds = HoldBook(accounts, ledger)
    val payments = PaymentEngine(
        accounts = accounts,
        ledger = ledger,
        idempotency = idempotency,
        holds = holds,
        outbox = outbox,
        audit = audit,
    )
}
