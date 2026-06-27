# Regenera Bank — BFFs e APIs de Canal

**Documento:** BFF-BASELINE-001  
**Estado técnico:** verificado  
**Responsável nominal declarado:** Don Paulo Ricardo  
**Assinatura institucional:** pendente de chave externa real

BFF não é core bancário.

Não calcula saldo.
Não decide fraude.
Não liquida Pix.
Não escreve no ledger.

Recebe intenção autenticada, reduz superfície, compõe resposta e preserva contexto. Quando a dependência responde `UNKNOWN`, o canal para. Repetir dinheiro no escuro não é resiliência.

## Fronteiras ativas

- `web-bff`: sessão de navegador, CSRF, composição de home e comandos com idempotência;
- `mobile-bff`: attestation, vínculo de dispositivo, nonce e confirmação de operação;
- `operations-bff`: identidade corporativa, maker-checker, privilégio temporário e trilha encadeada;
- `partner-api`: mTLS, escopo, quota, idempotência e webhook assinado;
- `open-finance-api`: consentimento, permissão, interação rastreável e minimização de dados;
- `shared`: dinheiro, erros, correlação, idempotência, resiliência e auditoria.

## Comandos

```bash
make validate
make test
make security
make build
make verify-release
make all
```

`make all` precisa terminar com código zero. Relatório não substitui comando.

## Limite institucional

A árvore comprova comportamento local, integridade e controles de fronteira. Certificados, diretório corporativo, WAF, secret manager, homologações externas e assinaturas ficam fora do ZIP. Onde falta integração real, o documento registra bloqueio. Não existe aprovação por decoração.
