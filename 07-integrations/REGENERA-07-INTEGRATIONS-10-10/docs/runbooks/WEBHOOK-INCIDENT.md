# Runbook — Incidente de webhook

**Documento:** INT-RUN-005  
**Severidade:** SEV2; SEV1 se houver efeito financeiro  
**Owner:** Integration Platform

## Sinais

Assinatura inválida, timestamp vencido, replay, aumento de rejeições ou payload fora de schema.

## Resposta

1. manter o evento rejeitado;
2. não desabilitar validação para recuperar fila;
3. confirmar segredo e relógio;
4. solicitar reenvio pelo canal formal;
5. deduplicar pelo identificador do evento;
6. reconciliar efeitos financeiros;
7. rotacionar segredo se houver suspeita de exposição.

## Encerramento

Fila processada, duplicidades em zero, segredo validado e causa registrada.
