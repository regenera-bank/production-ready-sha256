# ADR-002 — dinheiro em centavos como string

**Estado:** aceito

## Problema

JSON não distingue inteiro seguro de aproximação em ponto flutuante.
Centavo perdido no contrato aparece depois na conciliação.

## Decisão

Todo valor monetário usa:

- `currency` explícita;
- `amountCents` como string inteira;
- nenhuma unidade implícita;
- nenhuma representação `number`.

## Risco aceito

Consumidor precisa converter de forma explícita.
É trabalho adicional.
Perder precisão seria pior.
