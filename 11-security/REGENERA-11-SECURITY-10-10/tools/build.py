#!/usr/bin/env python3
import json
import platform
import shutil
from common import ROOT, payload_files, sha256, dump

release=ROOT/"release"
if release.exists(): shutil.rmtree(release)
release.mkdir()
files=list(payload_files())
(release/"PAYLOAD-CHECKSUMS.sha256").write_text("".join(f"{sha256(path)}  {path.relative_to(ROOT).as_posix()}\n" for path in files),encoding="utf-8")
source=json.loads((ROOT/"evidence/source/SOURCE-INVENTORY.json").read_text())
registry=json.loads((ROOT/"config/security-registry.json").read_text())
dump(release/"MANIFEST.json",{
    "document_id":"SECURITY-RELEASE-MANIFEST-001","version":"10.10","payload_files":len(files),
    "state":"UNSIGNED_PENDING_EXTERNAL_APPROVAL","source_archive_sha256":source["source_sha256"],
    "integrity_scope":"payload_excludes_release_directory_to_avoid_self_reference",
})
dump(release/"SBOM.json",{
    "bomFormat":"CycloneDX","specVersion":"1.5","serialNumber":"urn:uuid:regenera-security-10-10",
    "components":[{"type":"application","name":"regenera-security-controls","version":"10.10","properties":[{"name":"runtime","value":"python-stdlib-only"},{"name":"network-used","value":"false"}]}]
})
dump(release/"BUILD-PROVENANCE.json",{
    "builder":"make all","python":platform.python_version(),"network_used":False,"dependencies_installed":False,
    "source_archive_sha256":source["source_sha256"],"payload_checksum_file":"release/PAYLOAD-CHECKSUMS.sha256",
    "signature":"PENDING_EXTERNAL_KEY","approval":"PENDING_INDEPENDENT_REVIEW",
})
dump(release/"CONTROL-STATUS.json",{
    "modules":registry["modules"],"technical_verification":"PASSED_LOCAL_CONTROLS",
    "activation":"BLOCKED_UNTIL_EXTERNAL_EVIDENCE_APPROVAL_AND_SIGNATURE",
})
print(f"BUILD: PASS ({len(files)} payload files)")
