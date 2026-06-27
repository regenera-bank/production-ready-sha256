# Arquitetura do núcleo bancário

**Documento:** CBA-ARCH-001  
**Versão:** 1.0  
**Vigência técnica:** 2026-06-26  
**Owner declarado:** Don Paulo Ricardo

## 1. Regra central

Saldo não é entidade independente.
Saldo é projeção do razão.

A consequência é objetiva:

- nenhum serviço atualiza saldo diretamente;
- todo efeito financeiro nasce em lançamento balanceado;
- correção financeira cria compensação;
- lançamento postado não é reescrito;
- estado externo incerto vira `UNKNOWN`;
- `UNKNOWN` abre reconciliação e bloqueia repetição automática.

## 2. Componentes

### Money

Representa unidade mínima em inteiro assinado de 64 bits.
Moeda faz parte do valor.
Operação entre moedas diferentes falha antes de produzir resultado.

### Accounts

Mantém identidade, classe contábil, moeda e estado operacional.
Conta encerrada não retorna ao fluxo.
Bloqueio impede novos lançamentos.

### Ledger

Recebe comandos imutáveis e produz `JournalEntry` com no mínimo duas linhas.
Débitos e créditos precisam fechar no mesmo lançamento.
A chave de idempotência aponta para o primeiro resultado válido.

### Holds

Reserva reduz saldo disponível sem alterar o razão.
Consumo, liberação e expiração encerram a reserva.
Reserva encerrada não volta a ficar ativa.

### Idempotency

A chave carrega escopo, hash do payload, estado e referência de resposta.
Payload divergente sob a mesma chave é conflito.
Estado `UNKNOWN` não volta para execução por tentativa automática.

### Payments

O débito, o registro do pagamento, a outbox e a trilha precisam nascer como uma unidade lógica.
A referência relacional final deve usar uma única transação de banco.

### Pix

A chave recebedora é mascarada e indexada por HMAC.
O valor cru não pertence a logs nem a armazenamento operacional genérico.
O EndToEndId interno permanece estável em replay.

### Reconciliation

Reconciliação resolve fato externo com evidência.
Não é botão de retry.
Resultado rejeitado cria reversão compensatória.

### Audit Chain

Cada evento referencia o hash anterior.
Alteração retroativa quebra a cadeia.
A cadeia não substitui assinatura externa, retenção imutável nem controle de acesso.

## 3. Fronteiras

```text
Canais e BFFs
    ↓ intenção autenticada
Core Banking
    ↓ efeito financeiro autorizado
Ledger
    ↓ evento transacional
Outbox
    ↓ entrega assíncrona
Integrações externas
    ↓ confirmação, rejeição ou incerteza
Reconciliação
```

## 4. Persistência

As migrations PostgreSQL criam:

- contas;
- lançamentos;
- partidas;
- reservas;
- idempotência;
- pagamentos;
- Pix;
- outbox;
- casos de reconciliação;
- auditoria append-only.

A migration protege `POSTED` contra alteração e impede update/delete das partidas.
A validação de equilíbrio ocorre quando o lançamento muda de `DRAFT` para `POSTED`.

## 5. Consistência

| Risco | Controle |
|---|---|
| débito duplicado | chave idempotente + hash do payload |
| corrida de saldo | lock de conta no adaptador relacional |
| lançamento incompleto | finalização somente após partidas balanceadas |
| falha após débito | estado persistido + outbox + reconciliação |
| reversão destrutiva | partida compensatória |
| mistura de moeda | validação de domínio e constraint |
| evento sem efeito financeiro | outbox na mesma transação |
| efeito financeiro sem evento | outbox obrigatória na mesma transação |

## 6. Integrações ainda bloqueadas

A ativação produtiva depende de:

- repositório PostgreSQL transacional;
- controle de concorrência por linha;
- secret manager;
- HSM ou serviço de chaves;
- IAM e segregação operacional;
- telemetria corporativa;
- mensageria;
- homologação Pix;
- testes de restauração e desastre no ambiente-alvo;
- aprovação independente assinada.
