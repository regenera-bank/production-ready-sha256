# Runbook — transação UNKNOWN

**Documento:** RB-CONTRACT-002  
**RTO de decisão:** 15 minutos  
**Tolerância de efeito financeiro duplicado:** zero

## Regra

Não repetir comando financeiro.
Consultar idempotência, ledger, outbox e provedor.

## Procedimento

1. localizar por `correlationId` e `Idempotency-Key`;
2. conferir lançamento no ledger;
3. conferir evento no outbox;
4. consultar o provedor pela referência externa;
5. classificar como `SETTLED`, `FAILED_FINAL` ou `RECONCILIATION_REQUIRED`;
6. registrar evidência e decisão.

Sem prova externa e contábil, o estado continua UNKNOWN.
Ansiedade operacional não muda fato financeiro.
