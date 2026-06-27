---
id: OPS-DOC-LIFECYCLE-001
title: Ciclo de Vida Documental
owner: Documentation Governance
reviewers: Architecture, Security, Compliance
status: ACTIVE
version: 1.0.0
classification: INTERNAL
last_reviewed: 2026-06-26
next_review_due: 2026-09-26
source_of_truth: CANONICAL
---

# Ciclo de Vida Documental

```mermaid
stateDiagram-v2
  [*] --> DRAFT
  DRAFT --> ACTIVE: revisão independente
  ACTIVE --> SUPERSEDED: nova versão
  ACTIVE --> RETIRED: decisão formal
  DRAFT --> EXTERNAL_PENDING: dependência externa
  EXTERNAL_PENDING --> ACTIVE: evidência incorporada
```

Transição exige registro de motivo, ator e data. Documento `ACTIVE` com revisão vencida é inválido até nova revisão.
