# Regenera Contracts

**Documento:** CONTRACTS-BASELINE-001  
**Estado:** pronto para assinatura e revisão independente  
**Responsável declarado:** Don Paulo Ricardo

Contrato não é documentação decorativa.
É fronteira.

Canal pede.
Domínio decide.
Ledger registra.
Evento prova.

Este pacote concentra os contratos públicos e internos do Regenera Bank:

- OpenAPI para contas, pagamentos, Pix e identidade;
- AsyncAPI para eventos financeiros e de auditoria;
- JSON Schema para dinheiro, transação, idempotência, erro e trilha de auditoria;
- catálogo único de erros e remediações;
- política de compatibilidade;
- validação, testes de ruptura e build reproduzível.

## Comandos

```bash
make validate
make test
make security
make build
make verify-release
make all
```

Nenhum comando instala dependência.
O ambiente precisa de Python 3.11+, PyYAML e jsonschema.

## Regra de promoção

A árvore pode ser validada sem assinatura.
Publicação não.

O arquivo `release/APPROVAL-RECORD.yaml` mantém a promoção bloqueada até existir:

1. revisão independente;
2. assinatura criptográfica real;
3. referência do ticket de mudança;
4. hash do ZIP distribuído.

Assinatura inventada não protege contrato.
Só cria prova contra quem publicou.
