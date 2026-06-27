# KYC, AML e sanções

**Documento:** RISK-POL-001  
**Responsável:** Compliance Risk  
**Vigência:** 2026-06-26  
**Revisão:** trimestral

## Objetivo

impedir onboarding e transação sem diligência suficiente

## Escopo

clientes, contrapartes e transações

## Papéis

- executor: Risk Operations;
- owner: Compliance Risk;
- aprovador independente: autoridade designada e registrada;
- auditor: função sem permissão de alteração.

## Controles obrigatórios

- lista oficial precisa ter versão e data;
- sanção confirmada bloqueia;
- PEP exige diligência reforçada;
- provedor indisponível produz `UNKNOWN`;
- hit não é encerrado sem caso.

## Evidências

- entrada avaliada e hash do payload;
- regra e versão aplicadas;
- decisão, motivos e ator;
- caso e aprovação quando houver escalonamento;
- trilha de auditoria íntegra.

## Métricas

- hit crítico sem caso: 0;
- decisões sem motivo: 0;
- lista vencida: 0.

## Exceções

Exceção exige owner, aprovador independente, justificativa, prazo e evidência.
Exceção vencida bloqueia o controle.

## Revisão

Revisão trimestral e após incidente material, mudança normativa ou alteração de regra.

## Aprovação

Aprovação institucional e assinatura criptográfica permanecem externas ao pacote.
