# Runbook — estado UNKNOWN

**Severidade mínima:** SEV2  
**Owner:** data-platform  
**Meta de reconhecimento:** 15 minutos

## Declaração

Existe efeito externo sem confirmação local.
Não reprocessar.

## Procedimento

1. congelar o `event_id`;
2. preservar payload hash, offset e correlation id;
3. consultar fonte externa ou storage autoritativo;
4. reconciliar efeito;
5. marcar `COMMITTED` ou `FAILED_FINAL`;
6. registrar decisão e evidência.

## Abortar

Se a fonte autoritativa não responder, manter `UNKNOWN`.
Disponibilidade não autoriza duplicidade.
