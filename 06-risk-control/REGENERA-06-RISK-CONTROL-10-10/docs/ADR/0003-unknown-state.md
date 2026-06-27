# ADR-003 — indisponibilidade vira UNKNOWN

## Contexto

Falha de provedor não prova ausência de risco.

## Decisão

KYC, AML, sanções e fraude podem devolver `UNKNOWN`.
Operação crítica não é aprovada nesse estado.

## Consequência

Disponibilidade perde para integridade.
A fila de revisão cresce.
Dinheiro não passa no escuro.
