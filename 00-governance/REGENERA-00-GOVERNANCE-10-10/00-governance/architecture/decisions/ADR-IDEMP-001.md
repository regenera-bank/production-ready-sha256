# ADR — idempotência durável

**Documento:** ADR-IDEMP-001  
**Estado:** controlled  
**Autor responsável:** Don Paulo Ricardo  
**Owner operacional:** engineering-governance  
**Vigência:** 2026-06-26  
**Próxima revisão:** 2027-06-26  
**Ciclo máximo:** 365 dias


## Problema

Retry pode repetir efeito financeiro.

## Alternativas

- memória local;
- cache distribuído como fonte;
- registro relacional durável;
- deduplicação apenas no provedor.

## Decisão

Usar registro durável com namespace, fingerprint, estado, resultado e transição condicional. Cache pode acelerar. Não decide a verdade.

## Consequências

A operação precisa definir `UNKNOWN`, expiração, conflito de fingerprint e replay de resultado.

## Rollback

Desativar consumidor novo sem remover registros. Chave usada permanece prova.
