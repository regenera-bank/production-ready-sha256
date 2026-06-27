# ADR — ledger relacional append-only

**Documento:** ADR-LEDGER-001  
**Estado:** controlled  
**Autor responsável:** Don Paulo Ricardo  
**Owner operacional:** engineering-governance  
**Vigência:** 2026-06-26  
**Próxima revisão:** 2027-06-26  
**Ciclo máximo:** 365 dias


## Contexto

O sistema precisa registrar efeito financeiro, estorno e reconciliação sem editar história.

## Alternativas consideradas

1. banco relacional com partidas dobradas e linhas append-only;
2. event sourcing integral;
3. ledger especializado externo;
4. modelo híbrido com escrita interna e espelho externo.

## Decisão

Adotar ledger relacional append-only como fonte financeira inicial. Débito e crédito fecham na mesma transação. Correção ocorre por lançamento compensatório.

## Alternativas rejeitadas

Event sourcing integral amplia superfície operacional antes de existir capacidade madura de replay e versionamento. Serviço externo cria dependência de disponibilidade e portabilidade. Modelo híbrido duplica reconciliação sem necessidade comprovada.

## Riscos aceitos

Escala horizontal de escrita depende de particionamento futuro. Consultas históricas exigem índices e fechamento contábil disciplinado.

## Migração

Plano de contas, constraints, teste de balanço, backfill verificado e reconciliação paralela.

## Rollback

Lançamento já usado não é apagado. A mudança é desativada e o efeito financeiro é compensado.

## Critérios de revisão

Volume, latência, custo de reconciliação, necessidade multimoeda e requisitos de disponibilidade.
