# Padrão de métricas e limites operacionais

**Documento:** STD-METRICS-001  
**Estado:** controlled  
**Autor responsável:** Don Paulo Ricardo  
**Owner operacional:** engineering-governance  
**Vigência:** 2026-06-26  
**Próxima revisão:** 2026-12-23  
**Ciclo máximo:** 180 dias


## Indicadores mínimos

| Indicador | Limite | Janela | Fonte | Ação |
|---|---:|---|---|---|
| availability_target | 99,99% | 30 dias | plataforma de observabilidade | abrir problema de confiabilidade |
| financial_posting_p99 | 300 ms | 5 minutos | tracing do ledger | bloquear promoção regressiva |
| reconciliation_break_tolerance | 0 | intradiária | motor de reconciliação | declarar incidente financeiro |
| duplicate_financial_effect_tolerance | 0 | contínua | ledger + idempotência | contenção imediata |
| critical_patch_sla | 72 h | por vulnerabilidade | gestão de vulnerabilidade | escalonar ao CISO |
| rto | 60 min | por exercício | cronologia de recuperação | plano corretivo |
| rpo | 5 min | por exercício | ponto restaurado | bloquear aceite do DR |
| release_rollback_target | 15 min | por release | pipeline e incidente | revisar estratégia |
| sev1_acknowledgement | 5 min | por incidente | ferramenta de incidentes | escalonamento automático |
| sev1_executive_notification | 15 min | por incidente | timeline | acionar substituto |

Métrica sem fonte e owner é opinião. Não entra no painel executivo.
