# Crédito

**Documento:** RISK-POL-003  
**Responsável:** Credit Risk  
**Vigência:** 2026-06-26  
**Revisão:** trimestral

## Objetivo

decidir crédito com política verificável

## Escopo

propostas, limites e revisão

## Papéis

- executor: Credit Operations;
- owner: Credit Risk;
- aprovador independente: autoridade designada e registrada;
- auditor: função sem permissão de alteração.

## Controles obrigatórios

- KYC aprovado;
- AML limpo;
- sanção ausente;
- DTI e score dentro da política;
- override silencioso proibido.

## Evidências

- entrada avaliada e hash do payload;
- regra e versão aplicadas;
- decisão, motivos e ator;
- caso e aprovação quando houver escalonamento;
- trilha de auditoria íntegra.

## Métricas

- aprovação fora da política: 0;
- decisão sem dados de origem: 0;
- revisão vencida: 0.

## Exceções

Exceção exige owner, aprovador independente, justificativa, prazo e evidência.
Exceção vencida bloqueia o controle.

## Revisão

Revisão trimestral e após incidente material, mudança normativa ou alteração de regra.

## Aprovação

Aprovação institucional e assinatura criptográfica permanecem externas ao pacote.
