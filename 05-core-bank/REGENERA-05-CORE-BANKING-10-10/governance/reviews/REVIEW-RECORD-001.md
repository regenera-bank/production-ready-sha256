# Registro de revisão técnica

**Registro:** REVIEW-CORE-001  
**Data:** 2026-06-26  
**Autor e responsável declarado:** Don Paulo Ricardo  
**Revisor independente:** pendente

## Itens revisados

- invariantes monetárias;
- equilíbrio do ledger;
- reversão;
- idempotência;
- reserva e saldo disponível;
- concorrência;
- estado `UNKNOWN`;
- reconciliação;
- proteção de chave Pix;
- outbox;
- trilha de auditoria;
- migration relacional;
- controles de release.

## Resultado

A revisão interna aprovou a baseline para auditoria independente.
A promoção produtiva permanece bloqueada até revisão segregada e assinatura real.

## Questões ainda abertas

- escolha e configuração do cluster PostgreSQL;
- mecanismo de lock e isolamento no adaptador real;
- HSM e secret manager;
- mensageria e política de retry;
- homologação Pix;
- RTO e RPO observados;
- retenção jurídica;
- owner institucional definitivo por controle.
