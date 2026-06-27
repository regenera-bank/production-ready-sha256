# Runbook — Resultado financeiro UNKNOWN

**Documento:** INT-RUN-001  
**Severidade mínima:** SEV2  
**Owner:** Finance Operations  
**RTO de decisão:** 30 minutos

## Critério de declaração

- timeout ou perda de conexão depois do envio;
- resposta ambígua em operação financeira;
- divergência entre estado interno e consulta externa.

## Primeiros cinco minutos

1. bloquear repetição da chave de idempotência;
2. registrar operação, provedor, correlação e horário;
3. verificar se existe referência externa;
4. abrir incidente e fila de reconciliação;
5. preservar payload redigido e logs de transporte.

## Gates de decisão

- **CONFIRMADO EXTERNO:** marcar sucesso e registrar referência.
- **NÃO ENCONTRADO COM PROVA SUFICIENTE:** autorizar nova tentativa com nova decisão registrada.
- **DIVERGENTE:** manter bloqueio e escalar para Finance Operations.
- **SEM EVIDÊNCIA:** não repetir. escalar.

## Encerramento

O incidente só encerra quando estado interno, externo e contábil concordam. Toda correção financeira usa lançamento compensatório. Histórico não é editado.

## Evidências

- consulta externa;
- trilha de idempotência;
- comparação de reconciliação;
- decisão nominal;
- lançamento compensatório, quando houver.
