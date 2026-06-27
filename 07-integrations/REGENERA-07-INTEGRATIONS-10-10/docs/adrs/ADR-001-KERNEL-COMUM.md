# ADR-001 — Kernel comum para integrações

## Contexto

Quatorze integrações não podem carregar quatorze implementações diferentes de retry, idempotência e segurança.
Diferença nessa camada vira incidente difícil de comparar.

## Alternativas

1. cada adaptador implementa tudo;
2. SDK externo define o comportamento;
3. kernel comum com portas específicas.

## Decisão

Usar kernel comum para políticas de transporte e estado.
Adaptadores traduzem contratos. Não redefinem risco.

## Consequências

- comportamento uniforme;
- testes concentrados;
- menor liberdade para SDK de fornecedor;
- mudança do kernel exige revisão transversal.

## Critério de revisão

Revisar quando um provedor exigir semântica incompatível com `UNKNOWN`, idempotência ou autenticação definida aqui.
