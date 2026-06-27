from __future__ import annotations
import re

def lint_comments(text: str) -> list[str]:
    errors: list[str] = []
    for number, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if not stripped.startswith(("#", "//", "--")):
            continue
        body = stripped.lstrip("#/- ").strip()
        if len(body) > 160:
            errors.append(f"linha {number}:comentário longo")
        if re.search(r"([=*_#-])\1{7,}", stripped):
            errors.append(f"linha {number}:banner decorativo")
        term = "TO" + "DO"
        if term in body.upper():
            errors.append(f"linha {number}:pendência sem rastreio")
        if body.lower() in {"this function does something", "helper function", "utility"}:
            errors.append(f"linha {number}:comentário sem decisão")
    return errors
