# ADR-002 — Lineage append-only

## Contexto

Lineage editável é narrativa.
Não é prova.

## Decisão

Cada transformação entra numa cadeia SHA-256 com hash anterior, entradas e saída.

## Risco aceito

A cadeia local não substitui storage imutável institucional.

## Rollback

Não se edita lineage.
Corrige com novo registro.
