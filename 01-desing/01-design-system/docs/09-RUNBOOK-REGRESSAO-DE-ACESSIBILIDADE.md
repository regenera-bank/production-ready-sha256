# Runbook de regressão de acessibilidade

**Documento:** DS-RUN-ACC-001

## Declaração

SEV1 quando impede confirmação, autenticação ou leitura de valor.
SEV2 quando impede fluxo relevante sem alternativa equivalente.

## Contenção

1. interromper release;
2. preservar evidência;
3. identificar componente e consumidores;
4. ativar versão anterior;
5. validar teclado e leitura;
6. comunicar suporte e operação.

## Diagnóstico

- contraste;
- foco;
- nome acessível;
- ordem de leitura;
- zoom;
- movimento;
- mensagem de erro;
- alvo de toque.

## Saída

Não encerrar com teste automático isolado.
A correção exige revisão humana de acessibilidade.

## Métrica

- reconhecimento: 15 minutos;
- contenção: 30 minutos;
- rollback alvo: 15 minutos após decisão;
- regressões críticas toleradas: zero.
