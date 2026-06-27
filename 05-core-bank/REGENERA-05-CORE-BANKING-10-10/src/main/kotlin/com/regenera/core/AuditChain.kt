package com.regenera.core

import java.time.Instant

data class AuditEvent(
    val sequence: Long,
    val eventType: String,
    val actorId: String,
    val subjectId: String,
    val payload: Map<String, String>,
    val occurredAt: Instant,
    val previousHash: String,
    val eventHash: String,
)

class AuditChain {
    private val events = mutableListOf<AuditEvent>()

    @Synchronized
    fun append(
        eventType: String,
        actorId: String,
        subjectId: String,
        payload: Map<String, String>,
        occurredAt: Instant,
    ): AuditEvent {
        if (!eventType.matches(Regex("^[A-Z][A-Z0-9_]{2,79}$"))) {
            throw ValidationException("AUDIT_EVENT_INVALID", "Evento de auditoria inválido")
        }
        if (actorId.isBlank() || subjectId.isBlank()) {
            throw ValidationException("AUDIT_IDENTITY_REQUIRED", "Ator e objeto são obrigatórios")
        }
        val sequence = events.size.toLong() + 1L
        val previousHash = events.lastOrNull()?.eventHash ?: "0".repeat(64)
        val eventHash = hash(
            sequence,
            eventType,
            actorId,
            subjectId,
            payload,
            occurredAt,
            previousHash,
        )
        val event = AuditEvent(
            sequence,
            eventType,
            actorId,
            subjectId,
            payload.toSortedMap(),
            occurredAt,
            previousHash,
            eventHash,
        )
        events += event
        return event
    }

    @Synchronized
    fun events(): List<AuditEvent> = events.toList()

    @Synchronized
    fun verify(): Boolean = verify(events)

    companion object {
        fun verify(events: List<AuditEvent>): Boolean {
            var previousHash = "0".repeat(64)
            var expectedSequence = 1L
            for (event in events) {
                if (event.sequence != expectedSequence) return false
                if (event.previousHash != previousHash) return false
                val expectedHash = hash(
                    event.sequence,
                    event.eventType,
                    event.actorId,
                    event.subjectId,
                    event.payload,
                    event.occurredAt,
                    event.previousHash,
                )
                if (event.eventHash != expectedHash) return false
                previousHash = event.eventHash
                expectedSequence += 1L
            }
            return true
        }

        private fun hash(
            sequence: Long,
            eventType: String,
            actorId: String,
            subjectId: String,
            payload: Map<String, String>,
            occurredAt: Instant,
            previousHash: String,
        ): String = sha256(
            canonical(
                listOf(
                    sequence,
                    eventType,
                    actorId,
                    subjectId,
                    payload.toSortedMap(),
                    occurredAt,
                    previousHash,
                ),
            ),
        )
    }
}
