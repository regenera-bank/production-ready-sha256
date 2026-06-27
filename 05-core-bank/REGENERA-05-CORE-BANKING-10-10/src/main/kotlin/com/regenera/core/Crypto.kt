package com.regenera.core

import java.security.MessageDigest
import javax.crypto.Mac
import javax.crypto.spec.SecretKeySpec

internal fun sha256(value: String): String =
    MessageDigest.getInstance("SHA-256")
        .digest(value.toByteArray(Charsets.UTF_8))
        .joinToString("") { "%02x".format(it) }

internal fun hmacSha256(key: ByteArray, value: String): String {
    val mac = Mac.getInstance("HmacSHA256")
    mac.init(SecretKeySpec(key, "HmacSHA256"))
    return mac.doFinal(value.toByteArray(Charsets.UTF_8))
        .joinToString("") { "%02x".format(it) }
}

internal fun canonical(parts: Iterable<Any?>): String =
    parts.joinToString("|") { part ->
        when (part) {
            null -> "<null>"
            is Map<*, *> -> part.entries
                .sortedBy { it.key.toString() }
                .joinToString(",") { "${it.key}=${it.value}" }
            is Iterable<*> -> part.joinToString(",")
            else -> part.toString()
        }
    }
