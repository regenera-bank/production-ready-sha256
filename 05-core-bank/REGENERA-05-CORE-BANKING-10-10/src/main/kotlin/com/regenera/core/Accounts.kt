package com.regenera.core

import java.util.UUID

enum class AccountClass {
    ASSET,
    LIABILITY,
    EQUITY,
    REVENUE,
    EXPENSE,
}

enum class AccountStatus {
    OPEN,
    BLOCKED,
    CLOSED,
}

data class LedgerAccount(
    val id: UUID,
    val ownerId: UUID,
    val accountClass: AccountClass,
    val currency: Currency,
    val status: AccountStatus,
)

class AccountRegistry {
    private val accounts = linkedMapOf<UUID, LedgerAccount>()

    @Synchronized
    fun open(
        id: UUID,
        ownerId: UUID,
        accountClass: AccountClass,
        currency: Currency,
    ): LedgerAccount {
        if (accounts.containsKey(id)) {
            throw ConflictException(
                "ACCOUNT_ALREADY_EXISTS",
                "Conta já cadastrada: $id",
            )
        }

        val account = LedgerAccount(
            id = id,
            ownerId = ownerId,
            accountClass = accountClass,
            currency = currency,
            status = AccountStatus.OPEN,
        )
        accounts[id] = account
        return account
    }

    @Synchronized
    fun get(id: UUID): LedgerAccount =
        accounts[id] ?: throw NotFoundException(
            "ACCOUNT_NOT_FOUND",
            "Conta não encontrada: $id",
        )

    @Synchronized
    fun block(id: UUID): LedgerAccount = transition(id, AccountStatus.BLOCKED)

    @Synchronized
    fun reopen(id: UUID): LedgerAccount {
        val account = get(id)
        if (account.status != AccountStatus.BLOCKED) {
            throw StateTransitionException(
                "ACCOUNT_REOPEN_FORBIDDEN",
                "Somente conta bloqueada pode ser reaberta",
            )
        }
        return replace(account.copy(status = AccountStatus.OPEN))
    }

    @Synchronized
    fun close(id: UUID): LedgerAccount = transition(id, AccountStatus.CLOSED)

    @Synchronized
    fun requireOpen(id: UUID): LedgerAccount {
        val account = get(id)
        if (account.status != AccountStatus.OPEN) {
            throw StateTransitionException(
                "ACCOUNT_NOT_OPEN",
                "Conta não está aberta: $id",
            )
        }
        return account
    }

    @Synchronized
    fun all(): List<LedgerAccount> = accounts.values.toList()

    private fun transition(id: UUID, target: AccountStatus): LedgerAccount {
        val account = get(id)
        if (account.status == AccountStatus.CLOSED) {
            throw StateTransitionException(
                "ACCOUNT_CLOSED_IMMUTABLE",
                "Conta encerrada não volta para operação",
            )
        }
        return replace(account.copy(status = target))
    }

    private fun replace(account: LedgerAccount): LedgerAccount {
        accounts[account.id] = account
        return account
    }
}
