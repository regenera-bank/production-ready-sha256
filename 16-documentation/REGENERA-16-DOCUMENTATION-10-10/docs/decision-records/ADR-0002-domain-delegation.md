---
id: ADR-0002
title: ADR-0002 — Delegação de Domínios Lógicos
owner: Architecture
reviewers: Architecture, Security, Compliance
status: ACTIVE
version: 1.0.0
classification: INTERNAL
last_reviewed: 2026-06-26
next_review_due: 2026-09-26
source_of_truth: CANONICAL
---

# ADR-0002 — Delegação de Domínios Lógicos

## Contexto

Criar um serviço para cada capacidade aumenta acoplamento operacional e custo de governança.

## Decisão

Capacidades lógicas são delegadas a bounded contexts maiores quando compartilham dados, invariantes e ciclo de mudança. Onboarding pertence a Customers; sessão e device trust pertencem a Identity; saldo e extrato pertencem a Accounts/Ledger; consentimento pertence a Regulatory; casos pertencem a Risk/Operations.

## Limite

Delegação não autoriza acesso direto a tabelas nem elimina contratos entre domínios.
