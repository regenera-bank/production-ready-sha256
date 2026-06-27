# Runbook — rollback de release

**Documento:** RUN-ROLLBACK-001  
**Estado:** controlled  
**Autor responsável:** Don Paulo Ricardo  
**Owner operacional:** engineering-governance  
**Vigência:** 2026-06-26  
**Próxima revisão:** 2026-12-23  
**Ciclo máximo:** 180 dias


## Gatilhos

Erro financeiro, aumento de falha, violação de SLO, incompatibilidade de contrato, migração inconsistente ou segurança degradada.

## Decisão

Release Manager propõe. Incident Commander ou Change Authority autoriza. Autor da mudança não é o único aprovador.

## Procedimento

1. congelar promoção;
2. capturar versão, hash, métricas e logs;
3. interromper tráfego para a versão afetada;
4. restaurar artefato anterior pelo hash aprovado;
5. executar validação e reconciliação;
6. verificar filas, outbox e estado UNKNOWN;
7. reabrir tráfego progressivamente;
8. registrar tempo observado.

## Banco de dados

Rollback destrutivo é proibido quando remove história. Use forward fix, feature flag ou compensação. Migration reversível precisa ter sido ensaiada antes.

## Meta

Rollback operacional em até 15 minutos. Se a integridade financeira estiver incerta, o tráfego permanece bloqueado.
