# Política de gestão de mudança

**Documento:** POL-CHANGE-001  
**Estado:** controlled  
**Autor responsável:** Don Paulo Ricardo  
**Owner operacional:** engineering-governance  
**Vigência:** 2026-06-26  
**Próxima revisão:** 2026-12-23  
**Ciclo máximo:** 180 dias


## Objetivo

Controlar mudança sem trocar velocidade por cegueira.

## Responsabilidades

O autor prepara. O reviewer desafia. O owner responde pelo impacto. A Change Authority aprova promoção. Operações valida retorno.

## Evidências

Ticket, diff, classificação, testes, aprovações, hash, janela, resultado e validação pós-mudança.

## Métricas

- mudanças sem ticket: 0;
- retrospectivas emergenciais acima de 24 horas: 0;
- mudanças com rollback não testado: 0.

## Escopo

Código, configuração, contrato, schema, infraestrutura, política e procedimento operacional.

## Fluxo normal

1. ticket com motivo e impacto;
2. diff revisável;
3. classificação de risco;
4. teste proporcional;
5. aprovação segregada;
6. janela e comunicação;
7. execução observada;
8. validação pós-mudança;
9. fechamento com evidência.

## Mudança financeira

Exige teste de idempotência, reconciliação, estado desconhecido, rollback e ausência de efeito duplicado.

## Emergência

Incidente declarado pode encurtar o fluxo. Não elimina hash, registro de executor, resultado e retrospectiva em 24 horas.

## Bloqueios

Owner ausente, teste falho, evidência incompleta, aprovação própria ou rollback impossível bloqueiam a mudança.
