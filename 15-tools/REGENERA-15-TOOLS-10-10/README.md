# Regenera Tools

Toolkit controlado para validação, segurança, contratos, migrações, evidência e release.

A ferramenta não recebe autoridade implícita. Operação destrutiva começa em dry-run, exige aprovação explícita e permanece limitada ao workspace.

## Execução

```bash
make all
PYTHONPATH=src python3 -m regenera_tools.cli --help
```

## Estado

A verificação técnica local é reproduzível. Aprovação institucional, identidade central de CI e assinatura criptográfica permanecem pendentes de evidência externa.
