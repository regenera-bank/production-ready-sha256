---
id: ARCH-DEPENDENCY-MAP-001
title: Mapa de Dependências
owner: Architecture
reviewers: Architecture, Security, Compliance
status: ACTIVE
version: 1.0.0
classification: INTERNAL
last_reviewed: 2026-06-26
next_review_due: 2026-09-26
source_of_truth: CANONICAL
---

# Mapa de Dependências

## Regra

Dependência aponta para contrato, não para implementação privada.

| Origem | Dependência permitida | Dependência proibida |
|---|---|---|
| Channels | BFFs e Design System | banco, ledger ou integração direta |
| BFFs | Contracts e APIs de domínio | acesso direto a tabelas |
| Core Banking | Contracts, Platform e Integrations | UI e estado de sessão de canal |
| Risk Control | eventos e dados autorizados | mutação silenciosa do ledger |
| Data Platform | eventos versionados | captura sem contrato e finalidade |
| Operations | APIs operacionais | bypass de maker-checker |

Toda exceção precisa de owner, prazo, evidência e aprovação independente.
