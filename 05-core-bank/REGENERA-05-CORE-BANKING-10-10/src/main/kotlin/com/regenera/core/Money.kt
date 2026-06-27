package com.regenera.core

import java.math.BigInteger

// dinheiro não aceita aproximação.
// aqui dentro só existe inteiro em unidade mínima.
data class Currency private constructor(val code: String) {
    companion object {
        val BRL = Currency("BRL")

        fun of(code: String): Currency {
            val normalized = code.trim().uppercase()
            if (!normalized.matches(Regex("^[A-Z]{3}$"))) {
                throw ValidationException(
                    "CURRENCY_INVALID",
                    "Moeda inválida: $code",
                )
            }
            return Currency(normalized)
        }
    }
}

data class Money private constructor(
    val minorUnits: Long,
    val currency: Currency,
) : Comparable<Money> {

    fun plus(other: Money): Money {
        assertSameCurrency(other)
        return ofMinorUnits(Math.addExact(minorUnits, other.minorUnits), currency)
    }

    fun minus(other: Money): Money {
        assertSameCurrency(other)
        return ofMinorUnits(Math.subtractExact(minorUnits, other.minorUnits), currency)
    }

    fun multiply(factor: Long): Money =
        ofMinorUnits(Math.multiplyExact(minorUnits, factor), currency)

    fun percentageBasisPoints(basisPoints: Long): Money {
        val product = BigInteger.valueOf(minorUnits)
            .multiply(BigInteger.valueOf(basisPoints))
        val divisor = BigInteger.valueOf(10_000L)
        val quotient = product.divide(divisor)
        val remainder = product.remainder(divisor)

        val rounded = if (remainder.abs().multiply(BigInteger.TWO) >= divisor) {
            quotient + BigInteger.valueOf(product.signum().toLong())
        } else {
            quotient
        }

        return ofMinorUnits(rounded.longValueExact(), currency)
    }

    fun isPositive(): Boolean = minorUnits > 0

    fun isZero(): Boolean = minorUnits == 0L

    override fun compareTo(other: Money): Int {
        assertSameCurrency(other)
        return minorUnits.compareTo(other.minorUnits)
    }

    private fun assertSameCurrency(other: Money) {
        if (currency != other.currency) {
            throw ValidationException(
                "MONEY_CURRENCY_MISMATCH",
                "Mistura de moedas: ${currency.code} e ${other.currency.code}",
            )
        }
    }

    companion object {
        fun zero(currency: Currency = Currency.BRL): Money =
            Money(0L, currency)

        fun ofMinorUnits(
            minorUnits: Long,
            currency: Currency = Currency.BRL,
        ): Money = Money(minorUnits, currency)
    }
}
