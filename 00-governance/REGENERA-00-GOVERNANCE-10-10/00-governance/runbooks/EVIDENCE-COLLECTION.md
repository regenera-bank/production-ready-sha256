# Runbook — coleta de evidência

**Documento:** RUN-EVID-001  
**Estado:** controlled  
**Autor responsável:** Don Paulo Ricardo  
**Owner operacional:** governance-corporate  
**Vigência:** 2026-06-26  
**Próxima revisão:** 2026-12-23  
**Ciclo máximo:** 180 dias


## Procedimento

1. identificar fonte, owner e período;
2. coletar sem executar conteúdo desconhecido;
3. registrar comando, cwd, horário e exit code;
4. calcular SHA-256;
5. copiar para repositório restrito;
6. conferir hash da cópia;
7. registrar acesso;
8. separar bruto de análise;
9. aplicar retenção e legal hold quando requerido.

## Proibição

Não reescrever log bruto para deixá-lo legível. A leitura tratada nasce em arquivo separado.
