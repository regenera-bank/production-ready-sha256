---
id: ARCH-ENVIRONMENT-MAP-001
title: Mapa de Ambientes
owner: Platform Operations
reviewers: Architecture, Security, Compliance
status: ACTIVE
version: 1.0.0
classification: INTERNAL
last_reviewed: 2026-06-26
next_review_due: 2026-09-26
source_of_truth: CANONICAL
---

# Mapa de Ambientes

| Ambiente | Finalidade | Dados reais | Efeito financeiro | Evidência mínima |
|---|---|---:|---:|---|
| local | desenvolvimento isolado | não | não | testes locais |
| integration | contratos entre serviços | sintéticos | não | relatório de integração |
| staging | validação pré-release | mascarados | não | release candidate assinada |
| production | operação autorizada | sim | sim | aprovação, assinatura e observabilidade |
| disaster-recovery | continuidade | réplica controlada | condicional | exercício e reconciliação |

Nenhum ambiente é considerado ativo por existir nesta tabela.
