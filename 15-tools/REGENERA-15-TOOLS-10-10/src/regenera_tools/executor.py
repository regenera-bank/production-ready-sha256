from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import subprocess
from .errors import ExecutionDenied
from .paths import resolve_within

@dataclass(frozen=True, slots=True)
class CommandRequest:
    argv: tuple[str, ...]
    cwd: str = "."
    timeout_seconds: int = 30
    mutating: bool = False
    approved: bool = False
    dry_run: bool = True
    env: tuple[tuple[str, str], ...] = ()

@dataclass(frozen=True, slots=True)
class CommandResult:
    returncode: int
    stdout: str
    stderr: str
    executed: bool

class SafeExecutor:
    def __init__(self, root: Path, allowed: set[str], allowed_env: set[str] | None = None):
        self.root = root.resolve()
        self.allowed = set(allowed)
        self.allowed_env = set(allowed_env or set())

    def run(self, request: CommandRequest) -> CommandResult:
        if not request.argv or request.argv[0] not in self.allowed:
            raise ExecutionDenied("executável não autorizado")
        if not 1 <= request.timeout_seconds <= 300:
            raise ExecutionDenied("timeout fora do limite")
        env = dict(request.env)
        if set(env) - self.allowed_env:
            raise ExecutionDenied("variável de ambiente não autorizada")
        if request.mutating and (not request.approved or request.dry_run):
            return CommandResult(0, "DRY-RUN\n", "", False)
        cwd = self.root if request.cwd == "." else resolve_within(self.root, request.cwd)
        completed = subprocess.run(
            list(request.argv), cwd=cwd, capture_output=True, text=True,
            timeout=request.timeout_seconds, env=env or None, check=False
        )
        return CommandResult(completed.returncode, completed.stdout[:1048576], completed.stderr[:1048576], True)
