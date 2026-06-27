---
id: CAT-DOCUMENT-REGISTER-001
title: Registro Documental
owner: Documentation Governance
reviewers: Architecture, Security, Compliance
status: ACTIVE
version: 1.0.0
classification: INTERNAL
last_reviewed: 2026-06-26
next_review_due: 2026-09-26
source_of_truth: CANONICAL
---

# Registro Documental

O registro executável está em [`registry/documents.json`](../../registry/documents.json). Ele é gerado a partir dos metadados e validado contra todos os documentos canônicos.

## Estados

- `DRAFT`: em elaboração;
- `ACTIVE`: fonte de verdade vigente;
- `SUPERSEDED`: substituído por versão posterior;
- `RETIRED`: retirado sem substituto ativo;
- `EXTERNAL_PENDING`: depende de fonte ou aprovação externa.

Documento ausente do registro é órfão e bloqueia a release.
