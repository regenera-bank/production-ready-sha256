# Runbook — Indisponibilidade de provedor

**Documento:** INT-RUN-002  
**Severidade:** SEV1 ou SEV2 conforme criticidade  
**Owner:** Integration Platform / SRE

## Critério de declaração

- taxa de erro acima do limite por cinco minutos;
- circuit breaker aberto;
- falha de DNS, TLS, autenticação ou rota;
- confirmação do fornecedor.

## Ações

1. abrir incidente e identificar operações afetadas;
2. separar falha antes e depois do envio;
3. bloquear retry financeiro ambíguo;
4. ativar contingência somente se homologada;
5. comunicar canais e operações;
6. acompanhar fila e idade de `UNKNOWN`;
7. preservar amostras redigidas e métricas.

## Gates de decisão

- contingência só entra com teste vigente;
- retorno do provedor exige health check e operação de baixo risco;
- fila financeira só reabre após reconciliação do período afetado;
- retorno instável reabre o circuit breaker.

## Encerramento

Encerrar após estabilidade, reconciliação e confirmação de backlog. Produzir linha do tempo, impacto, causa, evidência e ação preventiva.
