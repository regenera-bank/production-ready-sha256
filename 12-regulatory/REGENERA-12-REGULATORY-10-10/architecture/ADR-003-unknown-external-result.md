# ADR-003 — Resultado externo ambíguo

Timeout depois do envio não autoriza repetição. O estado passa para `UNKNOWN`, o mesmo idempotency key fica bloqueado e a resolução ocorre por consulta ou reconciliação.
