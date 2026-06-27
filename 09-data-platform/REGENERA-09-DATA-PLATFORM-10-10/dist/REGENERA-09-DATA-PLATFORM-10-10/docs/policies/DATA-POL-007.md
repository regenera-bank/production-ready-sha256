# Política de reconciliação financeira

**Documento:** DATA-POL-007  
**Owner:** finance  
**Revisão:** trimestral  
**Estado:** vigente para esta baseline

## Objetivo

Impedir publicação de número financeiro sem fechamento.

## Escopo

Aplica-se a datasets, pipelines, jobs, streams, tabelas, relatórios e artefatos de dados incluídos nesta plataforma.

## Controles obrigatórios

- referência única;
- valor em centavos;
- moeda explícita;
- tolerância zero;
- break precisa de owner.

## Evidências

- arquivo de origem;
- arquivo de destino;
- relatório de breaks;
- aceite financeiro.

## Exceções

Exceção exige ticket, risco aceito, prazo máximo de 30 dias, owner e aprovador independente. Exceção vencida bloqueia operação.

## Violações

Violação crítica interrompe publicação. O incidente entra em trilha com causa, impacto, contenção e plano de correção.
