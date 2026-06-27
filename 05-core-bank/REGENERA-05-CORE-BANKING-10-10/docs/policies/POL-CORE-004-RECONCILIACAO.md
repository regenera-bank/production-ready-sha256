# Política de reconciliação

**Documento:** POL-CORE-004  
**Owner declarado:** Don Paulo Ricardo  
**Revisão:** semestral

## Objetivo

Resolver divergência sem duplicar efeito e sem apagar o caminho que levou ao problema.

## Controles

- quebra financeira tolerada: zero;
- caso `UNKNOWN` precisa de fila e SLA;
- resolução exige referência externa;
- compensação aponta para o lançamento original;
- caso não pode ser encerrado sem evidência;
- divergência repetida exige análise de causa;
- fechamento diário bloqueia quando existir quebra não aceita;
- ajuste manual exige maker-checker.

## Métricas

| Indicador | Limite |
|---|---:|
| quebra financeira não justificada | 0 |
| duplicidade de efeito | 0 |
| casos `UNKNOWN` acima do SLA | 0 |
| reconciliações sem evidência | 0 |
| reversões sem vínculo original | 0 |
