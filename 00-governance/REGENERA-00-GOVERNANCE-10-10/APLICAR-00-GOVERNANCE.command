#!/usr/bin/env bash
set -euo pipefail

SOURCE_DIR="$(cd "$(dirname "$0")" && pwd)/00-governance"
TARGET_ROOT="/Volumes/REGENERA BANK/regenera-bank"
TARGET_DIR="$TARGET_ROOT/00-governance"
STAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP_DIR="$TARGET_ROOT/99-archive/governance-backup-$STAMP"
STAGING_DIR="$TARGET_ROOT/.governance-staging-$STAMP"

python3 "$SOURCE_DIR/scripts/governance.py" validate
PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s "$SOURCE_DIR/tests" -p 'test_*.py' -v
python3 "$SOURCE_DIR/scripts/governance.py" security

mkdir -p "$STAGING_DIR"
cp -R "$SOURCE_DIR/." "$STAGING_DIR/"

if [ -d "$TARGET_DIR" ]; then
  mkdir -p "$(dirname "$BACKUP_DIR")"
  mv "$TARGET_DIR" "$BACKUP_DIR"
fi

mv "$STAGING_DIR" "$TARGET_DIR"
printf 'Governança aplicada. Backup: %s\n' "$BACKUP_DIR"
open "$TARGET_DIR"
