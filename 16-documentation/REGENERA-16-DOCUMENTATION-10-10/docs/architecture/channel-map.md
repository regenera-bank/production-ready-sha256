---
id: ARCH-CHANNEL-MAP-001
title: Mapa dos Canais
owner: Channel Architecture
reviewers: Architecture, Security, Compliance
status: ACTIVE
version: 1.0.0
classification: INTERNAL
last_reviewed: 2026-06-26
next_review_due: 2026-09-26
source_of_truth: CANONICAL
---

# Mapa dos Canais

| Canal | Fronteira | Controles mínimos |
|---|---|---|
| Web Banking | Web BFF | origem, CSRF, sessão, acessibilidade |
| Android | Mobile BFF | attestation, binding, nonce, biometria |
| iOS | Mobile BFF | App Attest, Keychain, nonce, biometria |
| Windows Operations | Operations BFF | identidade corporativa, MFA, maker-checker |
| Partner Portal | Partner API | mTLS, OAuth scope, quota, HMAC |

Nenhum canal movimenta dinheiro diretamente.
