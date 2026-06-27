# Release

**Documento:** ENG-POL-001  
**Responsável:** Engineering Governance  
**Vigência:** 2026-06-26  
**Revisão:** trimestral

## Objetivo

publicar somente artefato verificável

## Escopo

código, regras, documentos e evidência

## Papéis

- executor: Release Engineering;
- owner: Engineering Governance;
- aprovador independente: autoridade designada e registrada;
- auditor: função sem permissão de alteração.

## Controles obrigatórios

- testes verdes;
- validação verde;
- scan verde;
- manifesto fechado;
- hash externo;
- assinatura real antes da promoção.

## Evidências

- entrada avaliada e hash do payload;
- regra e versão aplicadas;
- decisão, motivos e ator;
- caso e aprovação quando houver escalonamento;
- trilha de auditoria íntegra.

## Métricas

- release sem hash: 0;
- arquivo fora do manifesto: 0;
- assinatura simulada: 0.

## Exceções

Exceção exige owner, aprovador independente, justificativa, prazo e evidência.
Exceção vencida bloqueia o controle.

## Revisão

Revisão trimestral e após incidente material, mudança normativa ou alteração de regra.

## Aprovação

Aprovação institucional e assinatura criptográfica permanecem externas ao pacote.
