# ADR-001 — identidade de workload sem segredo estático

## Contexto

Credencial longa em container transforma vazamento em acesso duradouro.

## Alternativas

1. segredo fixo em variável;
2. certificado distribuído manualmente;
3. identidade federada de curta duração;
4. credencial de nó compartilhada.

## Decisão

Usar identidade federada de curta duração, audience restrita e issuer validado.

## Rejeições

Segredo fixo e credencial compartilhada foram rejeitados por ampliar blast radius.
Certificado manual foi rejeitado por depender de rotação humana.

## Consequência

O provedor real continua bloqueante até existir evidência externa.
