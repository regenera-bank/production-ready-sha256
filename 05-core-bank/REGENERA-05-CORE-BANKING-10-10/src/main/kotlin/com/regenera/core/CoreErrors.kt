package com.regenera.core

open class CoreBankingException(
    val code: String,
    message: String,
) : RuntimeException(message)

class ValidationException(code: String, message: String) :
    CoreBankingException(code, message)

class ConflictException(code: String, message: String) :
    CoreBankingException(code, message)

class NotFoundException(code: String, message: String) :
    CoreBankingException(code, message)

class StateTransitionException(code: String, message: String) :
    CoreBankingException(code, message)
