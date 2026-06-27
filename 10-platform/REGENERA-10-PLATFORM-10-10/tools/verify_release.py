#!/usr/bin/env python3
from pathlib import Path
import hashlib, sys, json
from common import ROOT
release=ROOT/"release"; errors=[]
checksum=release/"PAYLOAD-CHECKSUMS.sha256"
if not checksum.is_file(): errors.append("checksums-missing")
else:
  for line in checksum.read_text().splitlines():
    expected, rel=line.split("  ",1); p=ROOT/rel
    if not p.is_file(): errors.append(f"missing:{rel}"); continue
    actual=hashlib.sha256(p.read_bytes()).hexdigest()
    if actual!=expected: errors.append(f"mismatch:{rel}")
manifest=json.loads((release/"MANIFEST.json").read_text()) if (release/"MANIFEST.json").is_file() else {}
if manifest.get("state")!="UNSIGNED_PENDING_EXTERNAL_APPROVAL": errors.append("release-state-invalid")
if errors: print("VERIFY-RELEASE: FAIL"); print("\n".join(errors)); sys.exit(1)
print(f"VERIFY-RELEASE: PASS ({manifest.get('payload_files',0)} payload files)")
