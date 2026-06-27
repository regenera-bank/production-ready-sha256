# Arquitetura de Integrações Externas

**Documento:** INT-ARCH-001  
**Estado:** baseline técnico  
**Responsável:** Don Paulo Ricardo

## Contexto

O banco controla o pedido até a fronteira.
Depois da fronteira, controla apenas evidência, timeout, correlação e decisão de repetir ou não.

## Camadas

```text
Domínio
  ↓
Porta de integração
  ↓
Kernel comum
  ├── idempotência
  ├── timeout
  ├── retry seguro
  ├── circuit breaker
  ├── telemetria redigida
  └── estado UNKNOWN
  ↓
Adaptador por provedor
  ↓
Transporte autenticado
  ↓
Provedor externo
  ↓
Reconciliação
```

## Regras de fronteira

1. O domínio não conhece SDK de fornecedor.
2. O adaptador não calcula saldo nem decide regra financeira.
3. Resultado ambíguo não vira falha comum.
4. Retry financeiro só ocorre quando existe prova de que nada foi enviado.
5. Chave de idempotência é comparada com o payload.
6. Segredo fica em secret manager; nunca em URL, arquivo ou log.
7. Certificado é validado por identidade e fingerprint.
8. Resposta externa entra por schema e allowlist.
9. Conciliação confirma o que o transporte não consegue provar.

## Estado UNKNOWN

`UNKNOWN` significa que o banco não sabe se o provedor executou o efeito.
Não é `FAILED`.
Não é `RETRYABLE`.
É fila de reconciliação com bloqueio de repetição.

## Ativação

Cada adaptador possui evidências externas próprias.
Sem contrato, certificado, homologação e teste de contingência, o status continua `BLOCKED_EXTERNAL`.
