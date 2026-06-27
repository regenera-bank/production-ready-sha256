# Runbook — revogação de acesso

**Documento:** RUN-ACCESS-001  
**Estado:** controlled  
**Autor responsável:** Don Paulo Ricardo  
**Owner operacional:** security-governance  
**Vigência:** 2026-06-26  
**Próxima revisão:** 2026-12-23  
**Ciclo máximo:** 180 dias


## Gatilhos

Desligamento, mudança de função, suspeita de comprometimento, exceção vencida ou uso incompatível.

## Procedimento

1. registrar autoridade e horário;
2. revogar sessão, token, chave e grupo;
3. bloquear conta de emergência relacionada;
4. rotacionar segredo compartilhado afetado;
5. preservar logs;
6. verificar uso posterior;
7. confirmar revogação em todos os sistemas;
8. encerrar com evidência.

SEV1 exige início imediato. Demais casos seguem SLA definido pelo risco e nunca excedem o fim do vínculo.
