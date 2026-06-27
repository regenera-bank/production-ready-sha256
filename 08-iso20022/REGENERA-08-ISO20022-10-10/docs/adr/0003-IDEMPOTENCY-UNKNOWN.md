# ADR 0003 — MsgId, digest e estado UNKNOWN

## Contexto
A rede pode aceitar a mensagem e perder a resposta.

## Decisão
`MsgId` identifica a intenção; SHA-256 identifica o conteúdo.
Mesmo `MsgId` e mesmo digest é replay.
Mesmo `MsgId` e outro digest é conflito.
Depois do envio, ausência de resposta produz `UNKNOWN`.

## Consequência
`UNKNOWN` bloqueia repetição cega e exige reconciliação.
