# Política de Retry, Idempotência e Estado UNKNOWN

**Documento:** INT-POL-002  
**Vigência técnica:** 26 de junho de 2026  
**Revisão:** semestral

## Objetivo

Impedir efeito financeiro duplicado e transformar ambiguidade de transporte em estado operacional tratável.

## Escopo

Aplica-se a toda operação externa mutável e a qualquer consulta que possa disparar efeito no fornecedor.

## Responsabilidades

- Core Banking define a chave de idempotência do caso de negócio.
- Integration Platform persiste fingerprint e resultado.
- Owner do adaptador classifica erros retryable e definitivos.
- Finance Operations reconcilia `UNKNOWN`.

## Controles obrigatórios

1. Chave de idempotência obrigatória em operação mutável.
2. Mesma chave com payload diferente gera conflito.
3. Replay devolve o primeiro resultado persistido.
4. Falha antes do envio pode repetir conforme política.
5. Falha depois do envio produz `UNKNOWN`.
6. Resposta financeira ambígua não recebe retry automático.
7. `UNKNOWN` bloqueia nova tentativa até reconciliação.
8. Circuit breaker limita falha em cascata.
9. Máximo de tentativas é explícito e limitado.
10. Toda reconciliação registra referência externa e decisão.

## Evidências

- testes de replay e conflito;
- teste de timeout antes e depois do envio;
- fila e idade de `UNKNOWN`;
- resultado da reconciliação;
- métrica de tentativas por provedor;
- registro de circuit breaker.

## Exceções

Operação sem idempotência só pode ser leitura comprovadamente sem efeito. A exceção precisa de owner, prazo e prova contratual do fornecedor.

## Revisão

Revisar semestralmente e após duplicidade, timeout ambíguo ou mudança de contrato do provedor.
