package com.regenera.core

import java.time.Instant
import java.util.UUID

data class OutboxEvent(
    val id: UUID,
    val aggregateType: String,
    val aggregateId: UUID,
    val eventType: String,
    val payload: Map<String, String>,
    val occurredAt: Instant,
    val publishedAt: Instant?,
)

class Outbox {
    private val events = linkedMapOf<UUID, OutboxEvent>()

    @Synchronized
    fun append(event: OutboxEvent): OutboxEvent {
        if (events.containsKey(event.id)) {
            throw ConflictException("OUTBOX_EVENT_ALREADY_EXISTS", "Evento já existe")
        }
        if (event.publishedAt != null) {
            throw ValidationException(
                "OUTBOX_EVENT_ALREADY_PUBLISHED",
                "Evento novo não pode nascer publicado",
            )
        }
        events[event.id] = event.copy(payload = event.payload.toSortedMap())
        return events.getValue(event.id)
    }

    @Synchronized
    fun pending(limit: Int): List<OutboxEvent> {
        if (limit !in 1..1000) {
            throw ValidationException("OUTBOX_LIMIT_INVALID", "Limite inválido")
        }
        return events.values.filter { it.publishedAt == null }.take(limit)
    }

    @Synchronized
    fun markPublished(id: UUID, at: Instant): OutboxEvent {
        val current = events[id] ?: throw NotFoundException(
            "OUTBOX_EVENT_NOT_FOUND",
            "Evento não encontrado",
        )
        val next = current.publishedAt?.let { current } ?: current.copy(publishedAt = at)
        events[id] = next
        return next
    }

    @Synchronized
    fun all(): List<OutboxEvent> = events.values.toList()
}
