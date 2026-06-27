---
id: CAT-EVENT-001
title: Catálogo de Eventos
owner: Event Governance
reviewers: Architecture, Security, Compliance
status: ACTIVE
version: 1.0.0
classification: INTERNAL
last_reviewed: 2026-06-26
next_review_due: 2026-09-26
source_of_truth: CANONICAL
---

# Catálogo de Eventos

| Evento | Produtor | Consumidores | Chave de deduplicação |
|---|---|---|---|
| ledger.posted | Core Banking | Data, Risk, Operations | posting_id |
| payment.status.changed | Payments | Channels, Operations | payment_id + version |
| pix.status.changed | Pix | Channels, Reconciliation | end_to_end_id + version |
| risk.case.opened | Risk Control | Operations, Regulatory | case_id |
| consent.changed | Regulatory | Open Finance, Audit | consent_id + version |

Eventos usam envelope versionado e nunca transportam segredo.
