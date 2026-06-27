# ADR-003 — Estado financeiro desconhecido

**Estado:** aceito  
**Data:** 2026-06-26  
**Responsável declarado:** Don Paulo Ricardo

## Contexto

Timeout não prova rejeição.
Conexão encerrada depois do envio não informa se o provedor recebeu.

## Decisão

Quando o resultado externo não puder ser determinado, a operação entra em `UNKNOWN`.
O fluxo automático não repete.
Uma reconciliação consulta evidência externa e decide o próximo estado.

## Alternativas rejeitadas

### Repetir até receber sucesso

Pode produzir duplicidade financeira.

### Marcar falha em todo timeout

Pode devolver dinheiro já liquidado e criar prejuízo em sentido contrário.

## Consequências

- operação precisa de fila operacional;
- alerta e SLA de reconciliação são obrigatórios;
- evidência externa precisa ser vinculada ao caso;
- resolução rejeitada cria reversão compensatória.
