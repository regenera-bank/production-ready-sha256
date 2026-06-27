# ADR-003 — estado UNKNOWN

**Estado:** aceito

## Contexto

Rede pode cair depois que o provedor aceitou.
Responder erro não desfaz o mundo externo.

## Decisão

`UNKNOWN` é estado formal.
Ele bloqueia repetição automática e abre reconciliação.

## Rejeitado

- tratar timeout como falha final;
- repetir até receber sucesso;
- esconder o estado do consumidor.

Retry cego depois de débito não é resiliência.
É duplicidade com nome bonito.
