# Runbook — indisponibilidade de dependência

**Severidade:** SEV-2; SEV-1 quando afeta operação financeira crítica  
**Reconhecimento:** 5 minutos  
**Notificação executiva SEV-1:** 15 minutos

1. Confirme falha por health técnico e erro real de chamada.
2. Abra circuit breaker para a dependência afetada.
3. Preserve leitura segura somente quando a fonte permitir dado conhecido e marcado.
4. Bloqueie comando financeiro sem confirmação.
5. Não altere timeout ou retry durante incidente sem registro de mudança.
6. Reabra tráfego em janela controlada.
7. Reconcilie comandos ambíguos antes de declarar recuperação.

Recuperar endpoint não encerra incidente. A fila de dúvida também precisa chegar a zero.
