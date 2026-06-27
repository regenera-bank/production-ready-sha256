# Ata de revisão técnica

**Documento:** INT-MINUTES-001  
**Revisor técnico:** Don Paulo Ricardo  
**Data:** 26 de junho de 2026

## Decisões

- falha depois do envio produz `UNKNOWN`;
- operação financeira ambígua não recebe retry automático;
- idempotência compara chave e fingerprint do payload;
- endpoint externo exige HTTPS e allowlist;
- webhook exige HMAC e janela temporal;
- reconciliação é obrigatória para divergência ou ausência;
- nenhum adaptador é marcado como produtivo sem homologação externa.

## Pendências bloqueantes

- revisão independente;
- assinatura GPG real;
- certificados e credenciais em secret manager;
- homologações específicas de cada provedor;
- teste de contingência em ambiente institucional.
