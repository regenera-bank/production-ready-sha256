# ADR — estado UNKNOWN

**Documento:** ADR-UNKNOWN-001  
**Estado:** controlled  
**Autor responsável:** Don Paulo Ricardo  
**Owner operacional:** engineering-governance  
**Vigência:** 2026-06-26  
**Próxima revisão:** 2027-06-26  
**Ciclo máximo:** 365 dias


## Contexto

Timeout não prova falha. Repetir cegamente pode duplicar dinheiro.

## Decisão

`UNKNOWN` é estado persistente. Bloqueia repetição automática até consulta, reconciliação ou decisão compensatória.

## Alternativas rejeitadas

Tratar timeout como falha cria duplicidade. Tratar como sucesso esconde perda. Retry ilimitado transfere risco ao provedor.

## Evidência

Evento de timeout, correlação, consulta ao provedor, decisão e resultado de reconciliação.
