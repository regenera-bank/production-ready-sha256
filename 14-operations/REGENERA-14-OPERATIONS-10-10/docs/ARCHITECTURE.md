# Arquitetura

O pacote implementa um plano de controle operacional sem acesso direto a bancos de domínio. Incidentes, mudanças, filas, reconciliação e continuidade compartilham somente tipos, evidência e políticas de autorização.

## Fronteiras

- o plano operacional não altera ledger;
- toda decisão privilegiada exige identidade e evidência;
- chamadas financeiras ambíguas entram em `UNKNOWN`;
- adaptadores externos ficam fora do núcleo;
- logs não transportam credenciais nem dados bancários brutos.
