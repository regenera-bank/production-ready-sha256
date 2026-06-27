# ADR 0003 — Sem recurso remoto em runtime

**Estado:** aceito  
**Data:** 2026-06-26  
**Responsável:** Don Paulo Ricardo

## Contexto

Fonte, ícone ou script remoto amplia indisponibilidade e cadeia de confiança.

## Alternativas

1. CDN pública;
2. CDN corporativa;
3. assets empacotados;
4. fallback remoto.

## Decisão

Empacotar assets necessários e usar fontes do sistema.

## Razões

Interface bancária não deve mudar porque terceiro publicou outra resposta no mesmo endereço.

## Consequências

O pacote cresce pouco e a release passa a controlar o hash.

## Rollback

Restaurar o pacote anterior completo.
