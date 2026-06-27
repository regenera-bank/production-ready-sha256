# Auditoria e evidência

**Documento:** CTRL-POL-002  
**Responsável:** Control Assurance  
**Vigência:** 2026-06-26  
**Revisão:** trimestral

## Objetivo

preservar prova íntegra e atribuível

## Escopo

decisões, casos, relatórios e exceções

## Papéis

- executor: Control Operations;
- owner: Control Assurance;
- aprovador independente: autoridade designada e registrada;
- auditor: função sem permissão de alteração.

## Controles obrigatórios

- evento é append-only;
- hash encadeado obrigatório;
- evidência possui SHA-256;
- maker não aprova;
- retenção segue decisão jurídica vigente.

## Evidências

- entrada avaliada e hash do payload;
- regra e versão aplicadas;
- decisão, motivos e ator;
- caso e aprovação quando houver escalonamento;
- trilha de auditoria íntegra.

## Métricas

- cadeia inválida: 0;
- evidência sem hash: 0;
- autoaprovação: 0.

## Exceções

Exceção exige owner, aprovador independente, justificativa, prazo e evidência.
Exceção vencida bloqueia o controle.

## Revisão

Revisão trimestral e após incidente material, mudança normativa ou alteração de regra.

## Aprovação

Aprovação institucional e assinatura criptográfica permanecem externas ao pacote.
