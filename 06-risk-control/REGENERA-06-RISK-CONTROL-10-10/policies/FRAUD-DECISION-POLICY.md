# Fraude

**Documento:** RISK-POL-002  
**Responsável:** Fraud Risk  
**Vigência:** 2026-06-26  
**Revisão:** trimestral

## Objetivo

conter fraude sem decisão muda

## Escopo

transações, dispositivos, sessão e beneficiário

## Papéis

- executor: Fraud Operations;
- owner: Fraud Risk;
- aprovador independente: autoridade designada e registrada;
- auditor: função sem permissão de alteração.

## Controles obrigatórios

- sinais têm origem e validade;
- score sempre acompanha motivos;
- `UNKNOWN` não aprova;
- bloqueio abre caso;
- regra alterada exige teste de regressão.

## Evidências

- entrada avaliada e hash do payload;
- regra e versão aplicadas;
- decisão, motivos e ator;
- caso e aprovação quando houver escalonamento;
- trilha de auditoria íntegra.

## Métricas

- duplicidade financeira: 0;
- bloqueio sem motivo: 0;
- sinal crítico indisponível fora do SLA: 0.

## Exceções

Exceção exige owner, aprovador independente, justificativa, prazo e evidência.
Exceção vencida bloqueia o controle.

## Revisão

Revisão trimestral e após incidente material, mudança normativa ou alteração de regra.

## Aprovação

Aprovação institucional e assinatura criptográfica permanecem externas ao pacote.
