---
id: ARCH-SYSTEM-CONTEXT-001
title: Contexto do Sistema
owner: Architecture
reviewers: Architecture, Security, Compliance
status: ACTIVE
version: 1.0.0
classification: INTERNAL
last_reviewed: 2026-06-26
next_review_due: 2026-09-26
source_of_truth: CANONICAL
---

# Contexto do Sistema

O Regenera Bank é organizado como um workspace de domínios independentes por risco. Canais nunca são fonte autoritativa de saldo. BFFs compõem respostas e aplicam controles de canal. O Core Banking mantém contas, ledger, transações e reconciliação. Risco, segurança, plataforma, integrações e regulação mantêm controles próprios.

```mermaid
flowchart TD
  Channels[Canais] --> Edge[Edge e identidade]
  Edge --> BFF[BFFs]
  BFF --> Core[Core Banking]
  Core --> Risk[Risco e controles]
  Core --> Integrations[Integrações]
  Core --> Data[Plataforma de dados]
  Platform[Plataforma] --> Core
  Security[Segurança] --> Platform
  Regulatory[Regulatório] --> Risk
  Operations[Operações] --> Core
```

## Invariantes

- dinheiro usa unidade mínima inteira;
- efeito financeiro exige idempotência;
- estado ambíguo vira `UNKNOWN`;
- `UNKNOWN` bloqueia repetição cega;
- reversão é compensatória;
- aprovação humana externa não é simulada.
