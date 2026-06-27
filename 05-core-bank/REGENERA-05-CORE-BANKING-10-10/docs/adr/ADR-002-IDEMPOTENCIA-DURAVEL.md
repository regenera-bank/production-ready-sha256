# ADR-002 — Idempotência durável

**Estado:** aceito  
**Data:** 2026-06-26  
**Responsável declarado:** Don Paulo Ricardo

## Contexto

Retry faz parte da rede.
Efeito financeiro duplicado não pode fazer parte do negócio.

## Decisão

A fonte de verdade da idempotência será relacional e durável.
A chave será única por escopo.
O hash do payload será persistido.

## Regras

- mesma chave e mesmo payload retornam o primeiro resultado;
- mesma chave e payload diferente geram conflito;
- `PROCESSING` exige lease e recuperação controlada;
- `UNKNOWN` bloqueia nova execução;
- cache pode acelerar leitura, mas não decide efeito financeiro.

## Alternativas rejeitadas

### Apenas Redis

Perda, expiração ou divergência de cluster não pode reabrir efeito financeiro já executado.

### Deduplicação pelo identificador do pagamento

Não cobre reenvio antes da criação do identificador definitivo nem conflito de payload.

## Consequências

- retenção precisa cobrir a janela de replay do negócio;
- chaves precisam ser rastreáveis sem conter segredo;
- transição de estado entra na mesma transação do efeito.
