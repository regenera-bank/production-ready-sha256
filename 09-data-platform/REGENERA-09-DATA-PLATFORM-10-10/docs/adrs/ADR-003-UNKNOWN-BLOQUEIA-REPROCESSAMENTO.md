# ADR-003 — UNKNOWN bloqueia reprocessamento

## Contexto

Timeout depois do envio não prova falha.
Repetir pode duplicar efeito.

## Decisão

Falha ambígua recebe estado `UNKNOWN` e só sai por reconciliação.

## Consequência

Disponibilidade perde para integridade.
Esse é o custo certo.
