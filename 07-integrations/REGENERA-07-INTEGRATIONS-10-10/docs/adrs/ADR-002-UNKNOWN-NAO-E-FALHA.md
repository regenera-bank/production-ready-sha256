# ADR-002 — Resultado desconhecido não é falha comum

## Contexto

Timeout depois do envio não prova rejeição.
Repetir pode duplicar dinheiro.

## Alternativas

1. repetir automaticamente;
2. marcar como falha;
3. registrar `UNKNOWN` e reconciliar.

## Decisão

Adotar `UNKNOWN` como estado persistente e bloqueante.

## Consequências

- fila operacional obrigatória;
- SLA de reconciliação;
- nenhuma repetição cega;
- métricas específicas para envelhecimento do estado.
