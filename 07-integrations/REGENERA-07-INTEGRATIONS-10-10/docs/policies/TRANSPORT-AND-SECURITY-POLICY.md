# Política de Transporte e Segurança de Integrações

**Documento:** INT-POL-001  
**Vigência técnica:** 26 de junho de 2026  
**Revisão:** anual ou após incidente crítico

## Objetivo

Definir os controles mínimos para qualquer tráfego entre o Regenera Bank e terceiros.

## Escopo

Aplica-se a APIs, webhooks, arquivos, mensageria, redes financeiras, bureaus, custodiante, correspondentes e canais regulatórios.

## Responsabilidades

- Integration Platform mantém o kernel e a allowlist.
- Security Engineering administra certificados, chaves e algoritmos.
- Owner do adaptador mantém contrato, schema e homologação.
- SRE responde por disponibilidade e circuit breaker.
- Finance Operations responde por reconciliação financeira.

## Controles obrigatórios

1. HTTPS obrigatório para transporte IP.
2. mTLS quando o provedor suportar ou exigir.
3. Host fixado em allowlist; redirecionamento externo é recusado.
4. Credencial não entra em URL, log, código ou pacote.
5. Webhook exige assinatura, timestamp e proteção contra replay.
6. Certificado vencido, revogado ou fora da fingerprint autorizada bloqueia conexão.
7. Payload de log usa allowlist; dado financeiro ou pessoal não entra por padrão.
8. Timeout possui orçamento explícito por operação.
9. Algoritmo criptográfico depende de política institucional vigente.

## Evidências

- inventário de certificados;
- configuração de allowlist;
- resultado de teste mTLS;
- teste de webhook adulterado e expirado;
- relatório de secret scan;
- registro de rotação;
- trilha de mudança aprovada.

## Exceções

Exceção exige prazo, risco, compensação, owner e aprovação independente de Security Engineering. Exceção vencida bloqueia o adaptador.

## Revisão

Revisão anual, após comprometimento de credencial, mudança de provedor ou alteração de algoritmo. A revisão produz ata, diff e referência de aprovação.
