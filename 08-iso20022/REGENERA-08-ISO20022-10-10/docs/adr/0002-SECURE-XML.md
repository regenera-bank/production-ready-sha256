# ADR 0002 — XML entra com limites e sem DTD

## Contexto
XML aceita construções que ampliam custo e superfície de ataque.

## Decisão
Bloquear DTD, entidades externas, profundidade, quantidade de elementos, bytes e texto acumulado.

## Alternativas rejeitadas
Parser irrestrito foi rejeitado.
Sanitização depois do parse foi rejeitada porque o dano acontece antes.

## Consequência
Mensagem fora do limite falha antes da regra de negócio.
