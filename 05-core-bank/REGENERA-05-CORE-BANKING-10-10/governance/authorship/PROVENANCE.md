# Procedência

## Origem recebida

O pacote de origem continha 36 módulos e 6.860 entradas compactadas.
Havia código ativo, estruturas repetidas, diretórios de presença, material histórico, pacotes internos e resíduos de sistema.

## Critério de consolidação

Foram mantidos apenas elementos necessários para comprovar o núcleo financeiro:

- Money;
- Accounts;
- Ledger;
- Holds;
- Idempotency;
- Payments;
- Pix;
- Outbox;
- Audit Chain;
- Reconciliation;
- migrations e controles associados.

Módulos sem comportamento comprovável não foram promovidos como implementação ativa.
Eles permanecem fora desta release e precisam de especificação própria.

## Cadeia desta entrega

1. inventário do ZIP recebido;
2. seleção das capacidades fundacionais;
3. implementação e revisão do domínio;
4. execução dos testes;
5. correção dos achados;
6. geração da evidência;
7. checksum da árvore final;
8. compactação determinística;
9. nova execução sobre extração limpa;
10. assinatura externa pendente.
