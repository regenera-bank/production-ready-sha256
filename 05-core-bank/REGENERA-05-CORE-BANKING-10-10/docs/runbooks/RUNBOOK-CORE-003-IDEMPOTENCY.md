# Runbook — falha de idempotência

**Severidade:** SEV-1 quando houver efeito financeiro duplicado  
**Owner operacional:** Core Banking Operations

## Sinais

- mesma chave ligada a dois efeitos;
- payload diferente aceito sob a mesma chave;
- registro expirado antes da janela de replay;
- perda do registro durável;
- divergência entre pagamento e ledger.

## Procedimento

1. bloquear o escopo da operação;
2. preservar registros e traces;
3. localizar todas as ocorrências da chave;
4. comparar hashes de payload;
5. medir efeitos no ledger e no provedor;
6. impedir novos retries;
7. criar compensação quando houver duplicidade confirmada;
8. reconciliar contas afetadas;
9. revisar retenção, lease e transação;
10. reabrir somente após teste de concorrência.

## Encerramento

A operação volta quando a mesma chave, sob concorrência, produzir exatamente um efeito financeiro e um resultado estável.
