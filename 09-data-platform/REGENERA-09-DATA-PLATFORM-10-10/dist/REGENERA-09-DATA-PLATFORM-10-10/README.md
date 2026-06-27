# Regenera Bank — Plataforma de Dados

**Documento:** DATA-BASELINE-001  
**Estado:** pronto para validação técnica; ativação produtiva condicionada  
**Responsável técnico declarado:** Don Paulo Ricardo

Dado não vira verdade porque entrou no lake.
Vira verdade quando tem contrato, dono, origem, qualidade e rastro.

Este pacote entrega uma base executável para ingestão, contratos, qualidade, lineage, privacidade, retenção, acesso, streaming, warehouse, reconciliação financeira e governança de modelos. Não declara operação produtiva de lakehouse, cluster, catálogo, warehouse, SIEM, HSM, IAM, ferramenta de BI ou provedor externo.

## Conteúdo

- contratos de dados versionados;
- ingestão idempotente;
- quarentena para registros inválidos;
- lineage encadeado por SHA-256;
- qualidade com critérios bloqueantes;
- classificação, mascaramento e tokenização;
- retenção, legal hold e descarte controlado;
- autorização por finalidade e prazo;
- processamento de streaming sem repetição cega;
- histórico SCD2 sem sobreposição;
- reconciliação financeira por referência, valor e moeda;
- governança de modelos e datasets;
- políticas, ADRs, runbooks, matriz de controles e evidência reproduzível.

## Execução

```bash
make all
```

O comando limpa, valida, testa, executa o scan de segurança, monta a release e confere todos os hashes.

## Limite

Catálogo não substitui ownership.
Dashboard não substitui reconciliação.
Backup que nunca foi restaurado é esperança. Não é controle.
