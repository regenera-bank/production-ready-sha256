# Política de qualidade de dados

**Documento:** DATA-POL-002  
**Owner:** data-quality  
**Revisão:** trimestral  
**Estado:** vigente para esta baseline

## Objetivo

Bloquear dado que não sustenta decisão.

## Escopo

Aplica-se a datasets, pipelines, jobs, streams, tabelas, relatórios e artefatos de dados incluídos nesta plataforma.

## Controles obrigatórios

- regra com severidade;
- falha bloqueante impede publicação;
- quarentena preserva registro e motivo;
- SLA de correção definido pelo owner.

## Evidências

- resultado por regra;
- volume rejeitado;
- ticket de correção;
- aceite do owner.

## Exceções

Exceção exige ticket, risco aceito, prazo máximo de 30 dias, owner e aprovador independente. Exceção vencida bloqueia operação.

## Violações

Violação crítica interrompe publicação. O incidente entra em trilha com causa, impacto, contenção e plano de correção.
