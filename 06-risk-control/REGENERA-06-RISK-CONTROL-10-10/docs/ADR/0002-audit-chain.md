# ADR-002 — cadeia de auditoria append-only

## Contexto

Registro editável é narrativa.
Auditoria precisa de prova.

## Decisão

Cada evento inclui hash anterior e hash próprio.
Alteração posterior quebra a cadeia.

## Risco aceito

SHA-256 não substitui assinatura externa nem armazenamento imutável.
Esses controles continuam obrigatórios na plataforma.
