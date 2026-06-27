# ADR 0004 — Digest usa XML normalizado

## Contexto
Espaço e ordem de atributos não podem criar outra identidade para a mesma mensagem.

## Decisão
Normalizar texto, atributos e estrutura antes do SHA-256.

## Limite
Isto não substitui XML Signature nem canonicalização exigida pelo parceiro.
A assinatura institucional continua externa.
