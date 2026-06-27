#!/usr/bin/env python3
from pathlib import Path
import json, platform, sys, shutil
from common import ROOT, payload_files, sha256, dump
release=ROOT/"release"
if release.exists(): shutil.rmtree(release)
release.mkdir()
files=list(payload_files())
checks=[]
for p in files: checks.append(f"{sha256(p)}  {p.relative_to(ROOT).as_posix()}")
(release/"PAYLOAD-CHECKSUMS.sha256").write_text("\n".join(checks)+"\n")
dump(release/"MANIFEST.json",{"document_id":"PLATFORM-RELEASE-MANIFEST-001","payload_files":len(files),"state":"UNSIGNED_PENDING_EXTERNAL_APPROVAL","source_archive_sha256":json.loads((ROOT/"evidence/source/SOURCE-INVENTORY.json").read_text())["source_sha256"]})
dump(release/"SBOM.json",{"bomFormat":"CycloneDX","specVersion":"1.5","components":[{"type":"application","name":"regenera-platform-controls","version":"10.10","properties":[{"name":"runtime","value":"python-stdlib-only"}]}]})
dump(release/"BUILD-PROVENANCE.json",{"builder":"make all","python":platform.python_version(),"source_tree":"payload checksums","network_used":False,"dependencies_installed":False,"signature":"PENDING_EXTERNAL_KEY"})
registry=json.loads((ROOT/"config/platform-registry.json").read_text())
dump(release/"CONTROL-STATUS.json",{"modules":registry["modules"],"activation":"BLOCKED_UNTIL_EXTERNAL_EVIDENCE_AND_SIGNATURE"})
print(f"BUILD: PASS ({len(files)} payload files)")
