# Política de contratos

**Documento:** CONTRACT-POLICY-001  
**Versão:** 1.0.0  
**Responsável declarado:** Don Paulo Ricardo  
**Revisão independente:** pendente  
**Vigência:** após assinatura

## Objetivo

Contrato impede interpretação criativa entre sistemas.
Quando produtor e consumidor discordam, o dinheiro paga a conta.

## Escopo

Aplica-se a OpenAPI, AsyncAPI, JSON Schema, catálogos de erro e artefatos derivados.

## Controles obrigatórios

1. contrato tem versão semântica;
2. mudança incompatível exige versão principal nova;
3. operação financeira mutável exige `X-Correlation-ID` e `Idempotency-Key`;
4. valor monetário usa string de centavos e moeda explícita;
5. `UNKNOWN` não é sucesso nem falha. É bloqueio de repetição e gatilho de reconciliação;
6. remoção de campo, enum, path ou evento exige relatório de impacto;
7. produtor não publica evento antes do commit;
8. consumidor precisa ser idempotente;
9. exemplo não pode carregar segredo, documento real ou dado pessoal;
10. publicação exige revisão independente e assinatura real.

## Evidência

- relatório de validação;
- testes de compatibilidade;
- manifesto e checksums;
- aprovação segregada;
- assinatura do artefato distribuído.

## Exceção

Exceção tem dono, motivo, vencimento e compensação.
Exceção vencida bloqueia publicação.

## Revisão

Trimestral e sempre que houver incidente de contrato, duplicidade financeira ou quebra de consumidor.
