# Política de lineage

**Documento:** DATA-POL-005  
**Owner:** data-governance  
**Revisão:** trimestral  
**Estado:** vigente para esta baseline

## Objetivo

Provar origem e transformação.

## Escopo

Aplica-se a datasets, pipelines, jobs, streams, tabelas, relatórios e artefatos de dados incluídos nesta plataforma.

## Controles obrigatórios

- registro append-only;
- hash de entrada e saída;
- operação identificada;
- alteração detectável.

## Evidências

- cadeia de lineage;
- verificação de integridade;
- versão do job.

## Exceções

Exceção exige ticket, risco aceito, prazo máximo de 30 dias, owner e aprovador independente. Exceção vencida bloqueia operação.

## Violações

Violação crítica interrompe publicação. O incidente entra em trilha com causa, impacto, contenção e plano de correção.
