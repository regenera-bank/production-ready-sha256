# Runbook — restauração do núcleo bancário

**RTO de referência:** 60 minutos  
**RPO de referência:** 5 minutos  
**Estado:** metas técnicas; validação no ambiente-alvo pendente

## Preparação

- identificar backup e cadeia de WAL;
- validar checksum e retenção;
- confirmar ponto de recuperação;
- isolar o ambiente restaurado;
- registrar início e responsáveis.

## Execução

1. restaurar banco base;
2. aplicar WAL até o ponto aprovado;
3. validar migrations;
4. executar equilíbrio global do ledger;
5. validar sequência e hash da auditoria;
6. comparar outbox e mensageria;
7. identificar operações `UNKNOWN`;
8. executar reconciliação;
9. medir RTO e RPO observados;
10. liberar somente após aprovação de Operações e Contabilidade.

## Critérios de reprovação

- quebra financeira diferente de zero;
- duplicidade criada pela restauração;
- evento publicado sem lançamento;
- lançamento sem evento esperado;
- trilha de auditoria inválida;
- perda superior ao RPO aprovado.
