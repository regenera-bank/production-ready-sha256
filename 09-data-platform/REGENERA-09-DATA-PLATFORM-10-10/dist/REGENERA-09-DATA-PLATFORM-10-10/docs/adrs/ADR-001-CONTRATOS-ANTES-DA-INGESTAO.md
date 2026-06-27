# ADR-001 — Contratos antes da ingestão

## Contexto

Dataset sem contrato muda em silêncio.
Silêncio em dado vira relatório errado com aparência de verdade.

## Alternativas

- inferir schema em runtime;
- aceitar qualquer payload e corrigir depois;
- exigir contrato versionado antes do primeiro commit.

## Decisão

Contrato versionado é obrigatório. Campo removido, tipo alterado ou classificação modificada exige major.

## Consequências

Produtor precisa publicar antes.
Consumidor ganha uma fronteira que consegue testar.
