# Regenera Platform — controles de infraestrutura e operação

**Documento:** PLATFORM-BASELINE-001  
**Estado:** baseline técnica verificada  
**Responsável pela submissão:** Don Paulo Ricardo  
**Assinatura criptográfica:** obrigatória antes da promoção

Plataforma não é pasta de Terraform.
É o conjunto de travas que impede uma release, uma credencial ou uma falha regional de virar dinheiro perdido.

Este pacote entrega controles executáveis e evidência reproduzível para:

- identidade de workload;
- gestão de secrets e chaves;
- supply chain e promoção de release;
- rede e segmentação;
- baseline de Kubernetes;
- bancos, cache e mensageria;
- observabilidade e resposta;
- backup, restauração e disaster recovery;
- exceções, aprovação segregada e cadeia de auditoria.

## Limite institucional

O pacote não afirma que conta cloud, cluster, HSM, KMS, SIEM, banco ou região de DR existem.
Sem evidência externa, o estado é bloqueado.
Configuração bonita não substitui ambiente homologado.

## Execução

```bash
make all
```

O comando limpa resíduos, valida a árvore, executa testes, procura segredos, gera a release interna e verifica todos os hashes.
