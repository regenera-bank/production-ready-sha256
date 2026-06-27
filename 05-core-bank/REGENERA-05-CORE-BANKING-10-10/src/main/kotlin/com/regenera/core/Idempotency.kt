package com.regenera.core

import java.time.Instant

enum class IdempotencyState {
    RECEIVED,
    PROCESSING,
    COMPLETED,
    FAILED_RETRYABLE,
    FAILED_FINAL,
    UNKNOWN,
    EXPIRED,
}

data class IdempotencyRecord(
    val scope: String,
    val key: String,
    val payloadHash: String,
    val state: IdempotencyState,
    val responseReference: String?,
    val updatedAt: Instant,
)

sealed interface IdempotencyBegin {
    data class Acquired(val record: IdempotencyRecord) : IdempotencyBegin
    data class Replay(val responseReference: String) : IdempotencyBegin
    data class Blocked(val state: IdempotencyState) : IdempotencyBegin
}

class IdempotencyRegistry {
    private val records = linkedMapOf<Pair<String, String>, IdempotencyRecord>()

    @Synchronized
    fun begin(
        scope: String,
        key: String,
        payloadHash: String,
        now: Instant,
    ): IdempotencyBegin {
        validate(scope, key, payloadHash)
        val index = scope to key
        val existing = records[index]

        if (existing == null) {
            val record = IdempotencyRecord(
                scope = scope,
                key = key,
                payloadHash = payloadHash,
                state = IdempotencyState.PROCESSING,
                responseReference = null,
                updatedAt = now,
            )
            records[index] = record
            return IdempotencyBegin.Acquired(record)
        }

        if (existing.payloadHash != payloadHash) {
            throw ConflictException(
                "IDEMPOTENCY_PAYLOAD_CONFLICT",
                "A chave já foi usada com outro payload",
            )
        }

        return when (existing.state) {
            IdempotencyState.COMPLETED -> IdempotencyBegin.Replay(
                existing.responseReference
                    ?: throw IllegalStateException("Resposta concluída sem referência"),
            )
            IdempotencyState.FAILED_RETRYABLE,
            IdempotencyState.EXPIRED,
            -> {
                val reacquired = existing.copy(
                    state = IdempotencyState.PROCESSING,
                    responseReference = null,
                    updatedAt = now,
                )
                records[index] = reacquired
                IdempotencyBegin.Acquired(reacquired)
            }
            else -> IdempotencyBegin.Blocked(existing.state)
        }
    }

    @Synchronized
    fun complete(
        scope: String,
        key: String,
        responseReference: String,
        now: Instant,
    ): IdempotencyRecord = transition(
        scope,
        key,
        allowed = setOf(IdempotencyState.PROCESSING),
        target = IdempotencyState.COMPLETED,
        responseReference = responseReference,
        now = now,
    )

    @Synchronized
    fun markUnknown(scope: String, key: String, now: Instant): IdempotencyRecord =
        transition(
            scope,
            key,
            allowed = setOf(IdempotencyState.PROCESSING),
            target = IdempotencyState.UNKNOWN,
            responseReference = null,
            now = now,
        )

    @Synchronized
    fun failRetryable(scope: String, key: String, now: Instant): IdempotencyRecord =
        transition(
            scope,
            key,
            allowed = setOf(IdempotencyState.PROCESSING),
            target = IdempotencyState.FAILED_RETRYABLE,
            responseReference = null,
            now = now,
        )

    @Synchronized
    fun failFinal(scope: String, key: String, now: Instant): IdempotencyRecord =
        transition(
            scope,
            key,
            allowed = setOf(IdempotencyState.PROCESSING),
            target = IdempotencyState.FAILED_FINAL,
            responseReference = null,
            now = now,
        )

    @Synchronized
    fun expire(scope: String, key: String, now: Instant): IdempotencyRecord =
        transition(
            scope,
            key,
            allowed = setOf(
                IdempotencyState.RECEIVED,
                IdempotencyState.FAILED_RETRYABLE,
                IdempotencyState.FAILED_FINAL,
            ),
            target = IdempotencyState.EXPIRED,
            responseReference = null,
            now = now,
        )

    @Synchronized
    fun get(scope: String, key: String): IdempotencyRecord? = records[scope to key]

    private fun transition(
        scope: String,
        key: String,
        allowed: Set<IdempotencyState>,
        target: IdempotencyState,
        responseReference: String?,
        now: Instant,
    ): IdempotencyRecord {
        val index = scope to key
        val current = records[index] ?: throw NotFoundException(
            "IDEMPOTENCY_RECORD_NOT_FOUND",
            "Registro de idempotência não encontrado",
        )
        if (current.state !in allowed) {
            throw StateTransitionException(
                "IDEMPOTENCY_TRANSITION_FORBIDDEN",
                "Transição ${current.state} -> $target não permitida",
            )
        }
        val next = current.copy(
            state = target,
            responseReference = responseReference,
            updatedAt = now,
        )
        records[index] = next
        return next
    }

    private fun validate(scope: String, key: String, payloadHash: String) {
        if (!scope.matches(Regex("^[a-z][a-z0-9:_-]{2,79}$"))) {
            throw ValidationException(
                "IDEMPOTENCY_SCOPE_INVALID",
                "Escopo de idempotência inválido",
            )
        }
        if (key.length !in 16..128) {
            throw ValidationException(
                "IDEMPOTENCY_KEY_INVALID",
                "Chave de idempotência deve ter entre 16 e 128 caracteres",
            )
        }
        if (!payloadHash.matches(Regex("^[a-f0-9]{64}$"))) {
            throw ValidationException(
                "IDEMPOTENCY_HASH_INVALID",
                "Hash de payload inválido",
            )
        }
    }
}
