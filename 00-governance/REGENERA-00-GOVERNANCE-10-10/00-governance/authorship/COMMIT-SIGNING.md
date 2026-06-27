# Procedimento de commits e release assinados

**Documento:** SIGNING-001  
**Estado:** controlled  
**Autor responsável:** Don Paulo Ricardo  
**Owner operacional:** engineering-governance  
**Vigência:** 2026-06-26  
**Próxima revisão:** 2027-06-26  
**Ciclo máximo:** 365 dias


## Commits

Use GPG ou SSH signing configurado no perfil real do responsável.

```bash
git config --get user.name
git config --get user.email
git config --get user.signingkey
git log --show-signature --format=fuller -n 20
```

Commit sem assinatura válida não atende ao controle de autoria.

## Release

Depois de verificar o ZIP:

```bash
shasum -a 256 REGENERA-00-GOVERNANCE-10-10.zip
gpg --detach-sign --armor REGENERA-00-GOVERNANCE-10-10.zip
```

A chave privada não entra no pacote.
