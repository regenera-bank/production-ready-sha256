---
id: ARCH-DEPLOYMENT-MAP-001
title: Mapa de Implantação
owner: Platform Architecture
reviewers: Architecture, Security, Compliance
status: ACTIVE
version: 1.0.0
classification: INTERNAL
last_reviewed: 2026-06-26
next_review_due: 2026-09-26
source_of_truth: CANONICAL
---

# Mapa de Implantação

A documentação define zonas lógicas, não comprova recursos provisionados.

```mermaid
flowchart LR
  Internet --> Edge
  Edge --> Channels
  Channels --> BFFs
  BFFs --> Services
  Services --> LedgerDB[(Ledger DB)]
  Services --> Bus[(Event Bus)]
  Services --> External[External Networks]
  Services --> Evidence[(Evidence Store)]
```

## Bloqueios externos

- contas cloud;
- cluster e rede;
- IAM e HSM/KMS;
- certificados e DNS;
- banco, mensageria e storage;
- ambiente de continuidade;
- homologação de redes externas.
