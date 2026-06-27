# Política de contratos de dados

**Documento:** DATA-POL-001  
**Owner:** data-governance  
**Revisão:** trimestral  
**Estado:** vigente para esta baseline

## Objetivo

Evitar mudança silenciosa de schema.

## Escopo

Aplica-se a datasets, pipelines, jobs, streams, tabelas, relatórios e artefatos de dados incluídos nesta plataforma.

## Controles obrigatórios

- contrato versionado antes da ingestão;
- compatibilidade testada;
- owner e classificação obrigatórios;
- versão publicada é imutável.

## Evidências

- contrato;
- fingerprint;
- resultado de compatibilidade;
- aprovação.

## Exceções

Exceção exige ticket, risco aceito, prazo máximo de 30 dias, owner e aprovador independente. Exceção vencida bloqueia operação.

## Violações

Violação crítica interrompe publicação. O incidente entra em trilha com causa, impacto, contenção e plano de correção.
