# Runbook — desequilíbrio contábil

**Severidade:** SEV-1  
**RTO de contenção:** 15 minutos  
**Tolerância:** zero

## Ação imediata

1. bloquear novas postagens no escopo afetado;
2. preservar logs, WAL, traces e evidências;
3. identificar primeiro lançamento divergente;
4. impedir fechamento contábil;
5. acionar Core Banking, Contabilidade, Segurança e Operações;
6. comparar banco primário, réplica e relatórios;
7. não editar lançamento existente;
8. construir correção compensatória revisada;
9. executar reconciliação integral do período;
10. liberar somente após aprovação segregada.

## Proibido

- update manual em posting;
- delete para “fechar a soma”;
- recomputar saldo escondendo a origem;
- liberar tráfego antes de medir o alcance.

## Evidência

- consulta que localizou a primeira quebra;
- hashes do dump lógico sanitizado;
- diff da correção;
- aprovação;
- resultado da reconciliação;
- causa raiz;
- ações preventivas.
