---
id: ADR-0001
title: ADR-0001 — Autoridade Documental Única
owner: Architecture
reviewers: Architecture, Security, Compliance
status: ACTIVE
version: 1.0.0
classification: INTERNAL
last_reviewed: 2026-06-26
next_review_due: 2026-09-26
source_of_truth: CANONICAL
---

# ADR-0001 — Autoridade Documental Única

## Contexto

A origem continha documentos de três linhas, cópias, PDFs grandes e material de referência com afirmações incompatíveis entre si.

## Decisão

Markdown versionado é a fonte de verdade. Binários podem existir apenas como evidência externa com procedência e hash. O registro documental é derivado dos metadados e deve cobrir todos os documentos canônicos.

## Consequências

- revisão por diff;
- links e metadados testáveis;
- menor risco de documento órfão;
- binários não verificáveis deixam de ser autoridade.
