# Política de governança de modelos

**Documento:** DATA-POL-008  
**Owner:** model-risk  
**Revisão:** trimestral  
**Estado:** vigente para esta baseline

## Objetivo

Impedir ativação de modelo sem prova.

## Escopo

Aplica-se a datasets, pipelines, jobs, streams, tabelas, relatórios e artefatos de dados incluídos nesta plataforma.

## Controles obrigatórios

- artefato e dataset por hash;
- métrica mínima;
- owner;
- aprovação independente;
- rollback definido.

## Evidências

- model card;
- dataset fingerprint;
- resultado de validação;
- aprovação assinada.

## Exceções

Exceção exige ticket, risco aceito, prazo máximo de 30 dias, owner e aprovador independente. Exceção vencida bloqueia operação.

## Violações

Violação crítica interrompe publicação. O incidente entra em trilha com causa, impacto, contenção e plano de correção.
