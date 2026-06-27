# ADR-002 — Idempotência e estado desconhecido

## Contexto

Timeout não prova falha. A dependência pode ter executado e perdido a resposta.

## Alternativas

- repetir automaticamente;
- considerar timeout como falha final;
- marcar `UNKNOWN` e reconciliar;
- delegar toda decisão ao cliente.

## Decisão

A chave idempotente prende payload e resultado. Falha ambígua vira `UNKNOWN`. Enquanto o estado não for reconciliado, nova execução fica bloqueada.

## Consequência

O usuário pode esperar. O banco não duplica efeito financeiro para parecer rápido.
