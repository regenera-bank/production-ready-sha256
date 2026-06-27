---
id: CAT-API-001
title: Catálogo de APIs
owner: API Governance
reviewers: Architecture, Security, Compliance
status: ACTIVE
version: 1.0.0
classification: INTERNAL
last_reviewed: 2026-06-26
next_review_due: 2026-09-26
source_of_truth: CANONICAL
---

# Catálogo de APIs

| API | Consumidor | Contrato | Operação mutável | Idempotência |
|---|---|---|---:|---:|
| Accounts | canais e parceiros autorizados | OpenAPI 3.1 | não | n/a |
| Payments | BFFs | OpenAPI 3.1 | sim | obrigatória |
| Pix | BFFs | OpenAPI 3.1 | sim | obrigatória |
| Identity | canais | OpenAPI 3.1 | sim | por fluxo |
| Operations | backoffice | OpenAPI 3.1 | sim | obrigatória |

A especificação executável pertence ao pacote `02-contracts`.
