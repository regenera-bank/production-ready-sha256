package com.regenera.core

import java.time.Instant
import java.util.UUID

enum class HoldStatus {
    ACTIVE,
    CONSUMED,
    RELEASED,
    EXPIRED,
}

data class Hold(
    val id: UUID,
    val accountId: UUID,
    val amount: Money,
    val reason: String,
    val status: HoldStatus,
    val createdAt: Instant,
    val expiresAt: Instant,
    val closedAt: Instant?,
)

class HoldBook(
    private val accounts: AccountRegistry,
    private val ledger: Ledger,
) {
    private val holds = linkedMapOf<UUID, Hold>()

    @Synchronized
    fun place(
        id: UUID,
        accountId: UUID,
        amount: Money,
        reason: String,
        createdAt: Instant,
        expiresAt: Instant,
    ): Hold {
        accounts.requireOpen(accountId)
        if (!amount.isPositive()) {
            throw ValidationException(
                "HOLD_AMOUNT_NOT_POSITIVE",
                "Reserva exige valor positivo",
            )
        }
        if (!expiresAt.isAfter(createdAt)) {
            throw ValidationException(
                "HOLD_EXPIRY_INVALID",
                "Expiração deve ocorrer depois da criação",
            )
        }
        if (holds.containsKey(id)) {
            throw ConflictException("HOLD_ALREADY_EXISTS", "Reserva já existe")
        }
        if (availableBalance(accountId, createdAt) < amount) {
            throw ConflictException(
                "HOLD_INSUFFICIENT_FUNDS",
                "Saldo disponível insuficiente para a reserva",
            )
        }
        val hold = Hold(
            id,
            accountId,
            amount,
            reason.trim(),
            HoldStatus.ACTIVE,
            createdAt,
            expiresAt,
            null,
        )
        holds[id] = hold
        return hold
    }

    @Synchronized
    fun consume(id: UUID, now: Instant): Hold = close(id, HoldStatus.CONSUMED, now)

    @Synchronized
    fun release(id: UUID, now: Instant): Hold = close(id, HoldStatus.RELEASED, now)

    @Synchronized
    fun expire(now: Instant): List<Hold> {
        val expired = mutableListOf<Hold>()
        for ((id, hold) in holds.toMap()) {
            if (hold.status == HoldStatus.ACTIVE && !hold.expiresAt.isAfter(now)) {
                val next = hold.copy(status = HoldStatus.EXPIRED, closedAt = now)
                holds[id] = next
                expired += next
            }
        }
        return expired
    }

    @Synchronized
    fun activeAmount(accountId: UUID, now: Instant): Money {
        val account = accounts.get(accountId)
        var total = Money.zero(account.currency)
        for (hold in holds.values) {
            if (
                hold.accountId == accountId &&
                hold.status == HoldStatus.ACTIVE &&
                hold.expiresAt.isAfter(now)
            ) {
                total = total.plus(hold.amount)
            }
        }
        return total
    }

    @Synchronized
    fun availableBalance(accountId: UUID, now: Instant): Money =
        ledger.signedBalance(accountId).minus(activeAmount(accountId, now))

    @Synchronized
    fun get(id: UUID): Hold = holds[id] ?: throw NotFoundException(
        "HOLD_NOT_FOUND",
        "Reserva não encontrada",
    )

    private fun close(id: UUID, target: HoldStatus, now: Instant): Hold {
        val current = get(id)
        if (current.status != HoldStatus.ACTIVE) {
            throw StateTransitionException(
                "HOLD_ALREADY_CLOSED",
                "Reserva já foi encerrada",
            )
        }
        val next = current.copy(status = target, closedAt = now)
        holds[id] = next
        return next
    }
}
