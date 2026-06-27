#!/usr/bin/env bash
set -euo pipefail

ZIP=${1:-}
KEY=${2:-finance@regenerabank.world}

if [[ -z "$ZIP" || ! -f "$ZIP" ]]; then
  echo "uso: tools/sign_release.sh <arquivo.zip> [identidade-gpg]" >&2
  exit 2
fi

command -v gpg >/dev/null 2>&1 || { echo "gpg ausente" >&2; exit 2; }
gpg --list-secret-keys "$KEY" >/dev/null 2>&1 || { echo "chave privada não encontrada: $KEY" >&2; exit 2; }

shasum -a 256 "$ZIP" > "$ZIP.sha256"
gpg --local-user "$KEY" --armor --detach-sign --output "$ZIP.asc" "$ZIP"
gpg --local-user "$KEY" --armor --detach-sign --output "$ZIP.sha256.asc" "$ZIP.sha256"
gpg --verify "$ZIP.asc" "$ZIP"
gpg --verify "$ZIP.sha256.asc" "$ZIP.sha256"

echo "assinatura: PASS"
