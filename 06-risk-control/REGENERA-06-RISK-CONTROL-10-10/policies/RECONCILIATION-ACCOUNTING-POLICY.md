# Reconciliação e contabilidade

**Documento:** CTRL-POL-001  
**Responsável:** Financial Control  
**Vigência:** 2026-06-26  
**Revisão:** trimestral

## Objetivo

garantir que fato financeiro e registro externo fechem

## Escopo

liquidação, razão e período contábil

## Papéis

- executor: Reconciliation Operations;
- owner: Financial Control;
- aprovador independente: autoridade designada e registrada;
- auditor: função sem permissão de alteração.

## Controles obrigatórios

- tolerância financeira: zero;
- quebra abre caso;
- período fechado não recebe lançamento;
- correção ocorre por estorno;
- referência duplicada invalida lote.

## Evidências

- entrada avaliada e hash do payload;
- regra e versão aplicadas;
- decisão, motivos e ator;
- caso e aprovação quando houver escalonamento;
- trilha de auditoria íntegra.

## Métricas

- quebra não tratada no SLA: 0;
- lançamento desequilibrado: 0;
- alteração de período fechado: 0.

## Exceções

Exceção exige owner, aprovador independente, justificativa, prazo e evidência.
Exceção vencida bloqueia o controle.

## Revisão

Revisão trimestral e após incidente material, mudança normativa ou alteração de regra.

## Aprovação

Aprovação institucional e assinatura criptográfica permanecem externas ao pacote.
