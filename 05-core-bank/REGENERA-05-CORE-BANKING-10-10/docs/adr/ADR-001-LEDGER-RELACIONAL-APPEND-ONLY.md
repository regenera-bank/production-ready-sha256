# ADR-001 — Ledger relacional append-only

**Estado:** aceito  
**Data:** 2026-06-26  
**Responsável declarado:** Don Paulo Ricardo

## Contexto

O núcleo precisa preservar partidas dobradas, consulta operacional, consistência transacional e prova de correção.

## Alternativas consideradas

1. banco relacional com lançamentos append-only;
2. event sourcing integral;
3. ledger especializado de terceiro;
4. modelo híbrido com duas fontes financeiras.

## Decisão

Usar banco relacional como fonte financeira primária.
Lançamentos postados são imutáveis.
Eventos saem por outbox.

## Razões

- transação atômica entre lançamento, pagamento e outbox;
- constraints no mesmo motor que persiste o dinheiro;
- recuperação e auditoria sem depender de replay integral;
- menor risco de duas fontes concorrentes de saldo.

## Alternativas rejeitadas

### Event sourcing integral

Aumenta custo de projeção, correção histórica e operação.
Pode ser útil em domínios específicos, mas não entra como única fonte contábil nesta etapa.

### Ledger externo

Cria dependência operacional e contratual no ponto mais sensível do banco.
Só pode ser reconsiderado com due diligence, SLA, portabilidade e teste de saída.

### Modelo híbrido com duas fontes

Duas verdades financeiras não produzem redundância.
Produzem disputa.

## Consequências

- migrations precisam ser tratadas como código crítico;
- reversão é compensatória;
- relatório financeiro deriva do razão;
- retenção e backup do banco são controles fundamentais.

## Critério de revisão

Revisar quando houver requisito de escala que o modelo atual não cumpra, mudança regulatória ou evidência operacional de limite do motor relacional.
