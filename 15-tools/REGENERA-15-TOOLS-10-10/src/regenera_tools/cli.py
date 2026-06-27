from __future__ import annotations
import argparse, json, sys
from pathlib import Path
from .contracts import lint_openapi, lint_asyncapi
from .migrations import Migration, validate_migrations
from .secrets import scan_text
from .workspace import validate_workspace

def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="regenera-tools")
    sub = p.add_subparsers(dest="command", required=True)
    for name in ("scan-secrets", "lint-openapi", "lint-asyncapi", "validate-migrations"):
        command = sub.add_parser(name)
        command.add_argument("path")
    command = sub.add_parser("validate-workspace")
    command.add_argument("path")
    command.add_argument("--require", action="append", default=[])
    return p

def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    path = Path(args.path)
    try:
        if args.command == "scan-secrets":
            errors = [f"{x.rule}:{x.line}" for x in scan_text(path.read_text(encoding="utf-8"))]
        elif args.command == "lint-openapi":
            errors = lint_openapi(json.loads(path.read_text(encoding="utf-8")))
        elif args.command == "lint-asyncapi":
            errors = lint_asyncapi(json.loads(path.read_text(encoding="utf-8")))
        elif args.command == "validate-migrations":
            errors = validate_migrations([Migration(p.name, p.read_text(encoding="utf-8")) for p in sorted(path.glob("*.sql"))])
        else:
            errors = validate_workspace(path, args.require)
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 2
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("PASS")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
