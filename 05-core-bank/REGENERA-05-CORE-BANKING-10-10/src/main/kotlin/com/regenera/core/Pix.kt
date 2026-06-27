package com.regenera.core

import java.security.SecureRandom
import java.time.Instant
import java.time.ZoneId
import java.time.format.DateTimeFormatter
import java.util.UUID

data class PixPayment(
    val paymentId: UUID,
    val internalEndToEndId: String,
    val receiverKeyMasked: String,
    val receiverKeyHash: String,
    val receiverIspb: String?,
)

class PixEngine(
    private val payments: PaymentEngine,
    private val ispb: String,
    private val keyHashSecret: ByteArray,
    private val random: SecureRandom = SecureRandom(),
) {
    private val pixByPayment = linkedMapOf<UUID, PixPayment>()

    init {
        if (!ispb.matches(Regex("^[0-9]{8}$"))) {
            throw ValidationException("PIX_ISPB_INVALID", "ISPB deve ter oito dígitos")
        }
        if (keyHashSecret.size < 32) {
            throw ValidationException("PIX_KEY_HASH_SECRET_WEAK", "Segredo HMAC insuficiente")
        }
    }

    @Synchronized
    fun create(
        command: CreatePaymentCommand,
        receiverKey: String,
        receiverIspb: String?,
    ): PixPayment {
        pixByPayment[command.paymentId]?.let { return it }
        validateKey(receiverKey)
        if (receiverIspb != null && !receiverIspb.matches(Regex("^[0-9]{8}$"))) {
            throw ValidationException("PIX_RECEIVER_ISPB_INVALID", "ISPB destinatário inválido")
        }
        val payment = payments.create(command)
        val pixPayment = PixPayment(
            paymentId = payment.id,
            internalEndToEndId = endToEndId(command.occurredAt),
            receiverKeyMasked = mask(receiverKey),
            receiverKeyHash = hmacSha256(keyHashSecret, receiverKey),
            receiverIspb = receiverIspb,
        )
        pixByPayment[payment.id] = pixPayment
        return pixPayment
    }

    private fun endToEndId(at: Instant): String {
        val stamp = DateTimeFormatter.ofPattern("yyyyMMddHHmm")
            .withZone(ZoneId.of("America/Sao_Paulo"))
            .format(at)
        val alphabet = "abcdefghijklmnopqrstuvwxyz0123456789"
        val suffix = buildString {
            repeat(11) {
                append(alphabet[random.nextInt(alphabet.length)])
            }
        }
        return "E$ispb$stamp$suffix"
    }

    private fun validateKey(key: String) {
        val clean = key.trim()
        if (clean.isEmpty() || clean.length > 128) {
            throw ValidationException("PIX_KEY_INVALID", "Chave Pix inválida")
        }
    }

    private fun mask(key: String): String {
        val clean = key.trim()
        if ('@' in clean) {
            val parts = clean.split('@', limit = 2)
            return "${parts[0].take(2)}***@${parts[1]}"
        }
        return if (clean.length <= 6) "***" else "${clean.take(3)}***${clean.takeLast(2)}"
    }
}
