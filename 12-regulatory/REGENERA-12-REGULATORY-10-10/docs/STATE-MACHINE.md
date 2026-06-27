# Máquina de estados

`DRAFT -> READY -> APPROVED -> SUBMITTED -> ACCEPTED`

Resultados externos ambíguos entram em `UNKNOWN`. Rejeição retorna para nova versão em `DRAFT`. Prazo vencido entra em `OVERDUE` sem apagar o estado e a evidência anteriores.
