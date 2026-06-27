# Runbook — Quebra de reconciliação

**Documento:** INT-RUN-004  
**Severidade:** SEV1 quando existe diferença financeira  
**Owner:** Finance Operations

## Critério

- valor divergente;
- moeda divergente;
- referência ausente;
- duplicidade de referência;
- arquivo ou janela incompleta.

## Procedimento

1. congelar fechamento afetado;
2. identificar primeira divergência;
3. separar ausência, duplicidade e diferença de valor;
4. bloquear compensação automática sem causa;
5. consultar evidência externa;
6. registrar ajuste por lançamento compensatório;
7. repetir a reconciliação integral.

## Encerramento

Tolerância financeira é zero. O período só fecha quando a soma das diferenças volta a zero e a decisão está aprovada.
