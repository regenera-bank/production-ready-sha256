# Runbook — publicação bloqueada por qualidade

**Severidade:** conforme impacto  
**Owner:** data-quality

## Procedimento

1. interromper promoção do dataset;
2. preservar amostra, regra, versão e contagem;
3. enviar registros inválidos para quarentena;
4. notificar produtor e owner;
5. corrigir na origem ou versionar contrato;
6. repetir a bateria completa.

Não se desliga regra para liberar dashboard.
Corrige-se a causa.
