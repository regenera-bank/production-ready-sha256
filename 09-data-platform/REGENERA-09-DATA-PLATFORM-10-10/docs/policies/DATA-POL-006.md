# Política de acesso privilegiado

**Documento:** DATA-POL-006  
**Owner:** security  
**Revisão:** trimestral  
**Estado:** vigente para esta baseline

## Objetivo

Conter acesso emergencial e administrativo.

## Escopo

Aplica-se a datasets, pipelines, jobs, streams, tabelas, relatórios e artefatos de dados incluídos nesta plataforma.

## Controles obrigatórios

- grant com prazo;
- finalidade explícita;
- break-glass com dois aprovadores;
- autoaprovação proibida;
- revisão posterior obrigatória.

## Evidências

- ticket;
- aprovadores;
- janela;
- trilha de comandos e consultas.

## Exceções

Exceção exige ticket, risco aceito, prazo máximo de 30 dias, owner e aprovador independente. Exceção vencida bloqueia operação.

## Violações

Violação crítica interrompe publicação. O incidente entra em trilha com causa, impacto, contenção e plano de correção.
