# Arquitetura da plataforma de dados

**Documento:** DATA-ARCH-001  
**Estado:** baseline técnica

## Fronteiras

```text
fontes
  -> contrato
  -> ingestão idempotente
  -> quarentena ou commit
  -> qualidade
  -> lineage
  -> lake/warehouse/stream
  -> reconciliação e consumo
```

## Princípios

1. Contrato vem antes do dado.
2. Registro inválido não some. Vai para quarentena com motivo.
3. Lineage é append-only.
4. Dado financeiro não usa ponto flutuante.
5. Estado ambíguo não autoriza repetição.
6. Retenção não vence legal hold.
7. Acesso precisa de finalidade e prazo.
8. Modelo precisa de versão, dataset, métrica, owner e aprovação.

## Limites

Este pacote prova comportamento local.
Não prova cluster, storage, throughput, alta disponibilidade ou homologação externa.
