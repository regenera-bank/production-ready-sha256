# Threat model

Riscos principais: autoaprovação, repetição de efeito, encerramento sem prova, adulteração de evidência, fila concorrente, runbook desatualizado, mudança fora de janela, vazamento em atendimento e falsa declaração de continuidade.

Controles: maker-checker, idempotência, hash encadeado, leases, versionamento imutável, allowlist, reconciliação e bloqueio de dependência externa.
