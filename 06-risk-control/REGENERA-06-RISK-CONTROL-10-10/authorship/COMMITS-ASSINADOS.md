# Commits assinados

O pacote não inventa histórico Git.

No repositório canônico, cada mudança deve ser commitada em unidade pequena,
revisada e assinada com a chave real do autor.

```bash
git config user.signingkey <FINGERPRINT_REAL>
git config commit.gpgsign true
git commit -S -m "RISK-001: registra decisão e evidência"
git log --show-signature -1
```

Sem assinatura válida, a procedência permanece pendente.
