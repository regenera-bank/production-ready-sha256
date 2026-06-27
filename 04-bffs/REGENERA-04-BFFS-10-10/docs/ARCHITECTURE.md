# Arquitetura dos BFFs

**Documento:** BFF-ARCH-001  
**Estado:** baseline técnica verificada

Canal não manda no dinheiro.

O BFF conhece jornada, sessão e forma de resposta. O domínio conhece regra financeira. O ledger conhece efeito contábil. Misturar isso economiza uma chamada e cria um incidente difícil de explicar.

## Fluxo

```text
Canal
  -> BFF específico
  -> API de domínio
  -> Ledger / integrações
  -> reconciliação
```

## Regras

1. Resposta financeira carrega origem e correlação.
2. Comando mutável exige idempotência.
3. Timeout depois do envio vira `UNKNOWN`.
4. `UNKNOWN` não repete automaticamente.
5. BFF não grava saldo, lançamento ou estado de liquidação.
6. Cache financeiro usa `no-store` por padrão.
7. Operação privilegiada exige identidade corporativa, privilégio vigente e segregação.
8. Parceiro entra por mTLS, escopo e quota.
9. Open Finance exige consentimento vigente e permissão exata.

## Dependências externas

Certificados, WAF, secret manager, diretório corporativo, provider de identidade e homologações não são simulados. A integração fica bloqueada até existir evidência externa.
