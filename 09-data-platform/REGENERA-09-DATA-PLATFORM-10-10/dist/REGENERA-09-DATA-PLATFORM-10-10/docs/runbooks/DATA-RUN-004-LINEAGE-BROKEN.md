# Runbook — quebra de lineage

**Severidade:** SEV2  
**Owner:** data-governance

## Procedimento

1. bloquear publicação dos derivados;
2. preservar a cadeia quebrada;
3. localizar primeiro hash divergente;
4. identificar job, versão e executor;
5. reconstruir a partir da última origem íntegra;
6. emitir novo lineage. O antigo não é editado.
