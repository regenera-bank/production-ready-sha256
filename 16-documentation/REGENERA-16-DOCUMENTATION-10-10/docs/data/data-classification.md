---
id: DATA-CLASSIFICATION-001
title: Classificação de Dados
owner: Data Governance
reviewers: Architecture, Security, Compliance
status: ACTIVE
version: 1.0.0
classification: CONFIDENTIAL
last_reviewed: 2026-06-26
next_review_due: 2026-09-26
source_of_truth: CANONICAL
---

# Classificação de Dados

| Classe | Exemplo | Tratamento mínimo |
|---|---|---|
| PUBLIC | material institucional aprovado | integridade e owner |
| INTERNAL | arquitetura e processos | acesso corporativo |
| CONFIDENTIAL | controles, topologia e clientes | mínimo privilégio, criptografia e logging |
| RESTRICTED | segredo, chave, dado financeiro sensível | cofre/HSM, acesso JIT e dupla aprovação |

Segredo real e dado pessoal real são proibidos neste repositório documental.
