class Iso20022Error(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


class ValidationError(Iso20022Error):
    pass


class SecurityError(Iso20022Error):
    pass


class IdempotencyConflict(Iso20022Error):
    pass
