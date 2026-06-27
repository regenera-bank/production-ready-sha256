# Runbook — estado desconhecido

**Severidade mínima:** SEV-2  
**RTO de decisão:** 30 minutos  
**Tolerância a efeito financeiro duplicado:** zero

## Declaração

Abra incidente quando uma operação mutável terminar sem resposta conclusiva depois de alcançar a dependência.

## Contenção

1. Bloqueie repetição para a mesma chave e payload.
2. Preserve correlation id, idempotency key e horário.
3. Consulte a fonte autoritativa da operação.
4. Consulte ledger e outbox.
5. Não use log do BFF como prova de liquidação.

## Decisão

- efeito confirmado: grave o resultado original e encerre `UNKNOWN`;
- efeito ausente e ausência comprovada: libere nova tentativa com nova evidência;
- divergência: mantenha bloqueio e acione reconciliação.

## Encerramento

O incidente encerra somente com estado autoritativo, prova anexada e verificação de duplicidade zero.
