# Ata de revisão técnica

**Registro:** DATA-REVIEW-2026-001  
**Autor e responsável técnico declarado:** Don Paulo Ricardo  
**Data:** 2026-06-26  
**Estado:** revisão técnica concluída; aprovação institucional pendente

## Decisões

1. A árvore ativa não carrega `source-material`, arquivos de presença ou releases internas.
2. Ingestão só confirma efeito depois de validar contrato e qualidade.
3. Falha ambígua vira `UNKNOWN`. Não existe repetição cega.
4. PII exige finalidade, classificação e trilha.
5. Legal hold bloqueia descarte.
6. Resultado financeiro exige reconciliação com tolerância zero em centavos.
7. Modelo analítico não entra em produção sem dataset, versão, métrica, aprovação e rollback.

## Pendências institucionais

- nomeação de owners corporativos;
- revisão jurídica de retenção e base legal;
- assinatura criptográfica;
- integração com IAM, catálogo, storage, mensageria e observabilidade;
- exercício real de backup e recuperação em ambiente institucional.
