# Histórico de alterações

## 1.0.0 — 2026-06-26

- consolidação do núcleo financeiro verificável;
- implementação de Money, Accounts, Ledger, Holds, Idempotency, Payments, Pix, Outbox e Audit Chain;
- inclusão de 47 testes de risco;
- inclusão de migrations PostgreSQL com proteção de imutabilidade;
- inclusão de políticas, ADRs, matriz de controles e runbooks;
- remoção de estruturas vazias, resíduos de sistema e pacotes internos;
- geração de manifesto, SBOM, proveniência e checksums.

## 0.3.0 — 2026-06-26

- correção de replay Pix;
- integração de reservas ao saldo disponível de pagamento;
- limitação da chave interna de idempotência do ledger;
- falha de pagamento passa a encerrar o registro de idempotência.

## 0.2.0 — 2026-06-26

- implementação dos testes de concorrência, reversão e reconciliação;
- inclusão da trilha SHA-256 e outbox idempotente.

## 0.1.0 — 2026-06-26

- inventário do pacote de origem;
- definição do escopo ativo;
- registro das invariantes financeiras.
