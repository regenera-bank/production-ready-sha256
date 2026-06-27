# Runbook — indisponibilidade de fornecedor

**Documento:** RUN-VENDOR-001  
**Estado:** controlled  
**Autor responsável:** Don Paulo Ricardo  
**Owner operacional:** continuity-management  
**Vigência:** 2026-06-26  
**Próxima revisão:** 2026-12-23  
**Ciclo máximo:** 180 dias


## Objetivo

Conter dependência externa sem repetir efeito financeiro nem inventar sucesso.

## Procedimento

1. confirmar escopo e canal oficial do fornecedor;
2. suspender retries cegos;
3. classificar operações em concluída, falha ou UNKNOWN;
4. ativar fallback aprovado quando existir;
5. enfileirar reconciliação;
6. comunicar impacto e limite operacional;
7. retomar por lote controlado;
8. reconciliar antes do encerramento.

## Gate

Sem prova do resultado externo, a operação fica em UNKNOWN. Não é reenviada por conveniência.
