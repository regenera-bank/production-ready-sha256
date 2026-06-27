class ToolError(Exception):
    """Falha controlada de uma ferramenta."""
class ValidationError(ToolError): pass
class SecurityError(ToolError): pass
class IntegrityError(ToolError): pass
class ExecutionDenied(ToolError): pass
