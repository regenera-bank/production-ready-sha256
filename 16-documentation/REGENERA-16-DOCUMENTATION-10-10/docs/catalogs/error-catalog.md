---
id: CAT-ERROR-001
title: Catálogo de Erros
owner: API Governance
reviewers: Architecture, Security, Compliance
status: ACTIVE
version: 1.0.0
classification: INTERNAL
last_reviewed: 2026-06-26
next_review_due: 2026-09-26
source_of_truth: CANONICAL
---

# Catálogo de Erros

| Código | HTTP | Significado | Ação segura |
|---|---:|---|---|
| AUTH_REQUIRED | 401 | autenticação ausente ou inválida | autenticar novamente |
| FORBIDDEN | 403 | permissão insuficiente | solicitar acesso formal |
| IDEMPOTENCY_CONFLICT | 409 | mesma chave, outro payload | não repetir; investigar |
| INSUFFICIENT_FUNDS | 422 | saldo disponível insuficiente | corrigir valor ou aguardar |
| RESULT_UNKNOWN | 409 | resultado financeiro ambíguo | bloquear repetição e reconciliar |
| RATE_LIMITED | 429 | quota excedida | respeitar `Retry-After` |
| DEPENDENCY_UNAVAILABLE | 503 | dependência indisponível | retry apenas quando comprovadamente seguro |

Payload detalhado e schemas pertencem ao pacote `02-contracts`.
