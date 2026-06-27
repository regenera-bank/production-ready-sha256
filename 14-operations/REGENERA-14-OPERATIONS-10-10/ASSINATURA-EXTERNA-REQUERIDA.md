# Assinatura externa requerida

A árvore interna não contém chave privada nem assinatura fabricada.

A unidade de distribuição deve receber assinatura destacada OpenPGP depois da verificação final:

```bash
gpg --armor --detach-sign REGENERA-14-OPERATIONS-10-10.zip
```

O fingerprint, o titular da chave e a política de custódia devem acompanhar o registro de release.
