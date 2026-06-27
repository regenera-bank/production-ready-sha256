# ADR-004 — Checksum sem autorreferência

## Contexto

Arquivo não consegue provar o próprio hash sem criar ciclo.

## Decisão

Checksums internos cobrem todo o payload, menos o próprio arquivo. O hash externo do ZIP cobre a entrega completa.
