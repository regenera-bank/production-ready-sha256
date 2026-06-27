# Regenera Core Banking

**Pacote:** REGENERA-05-CORE-BANKING-10-10  
**Estado:** baseline técnica validada para integração controlada  
**Responsável técnico declarado:** Don Paulo Ricardo  
**Data de referência:** 2026-06-26

Core bancário não é coleção de endpoints.
É a parte que precisa continuar correta quando rede, operador e fornecedor deixam de colaborar.

Este pacote entrega uma base executável para:

- dinheiro em unidade mínima;
- contas contábeis;
- razão de partidas dobradas;
- reservas;
- idempotência;
- pagamentos;
- Pix;
- outbox;
- trilha encadeada;
- estado `UNKNOWN`;
- reconciliação;
- reversão compensatória.

## O que foi comprovado

A bateria local verifica, entre outros riscos:

- lançamento sem equilíbrio é recusado;
- moeda não se mistura dentro do mesmo lançamento;
- linha contábil exige valor positivo;
- duplicidade retorna o resultado original;
- payload divergente sob a mesma chave é bloqueado;
- lançamento postado preserva hash imutável;
- reversão cria nova partida compensatória;
- segunda reversão é recusada;
- reserva reduz saldo disponível;
- pagamento respeita reserva ativa;
- saldo insuficiente bloqueia débito;
- concorrência sob a mesma chave produz um único efeito financeiro;
- estado `UNKNOWN` bloqueia repetição cega;
- reconciliação pode concluir liquidação ou produzir reversão;
- chave Pix não permanece em claro;
- replay Pix preserva o mesmo EndToEndId;
- adulteração da trilha de auditoria é detectada.

## O que este pacote não afirma

Este artefato não declara:

- homologação no SPI ou DICT;
- operação com banco de dados produtivo;
- integração com HSM, secret manager ou IAM corporativo;
- aprovação jurídica ou regulatória;
- certificação de continuidade;
- autorização para movimentar recursos reais.

Essas etapas exigem ambiente, responsáveis, credenciais, contratos e evidências externas.
Inventar qualquer uma delas seria pior que deixar o bloqueio explícito.

## Execução

Requisitos:

- Java 21;
- Kotlin 1.9 ou superior;
- Python 3.11 ou superior;
- GNU Make.

Comandos:

```bash
make validate
make test
make security
make build
make verify-release
make all
```

`make all` precisa terminar com código de retorno zero.
Sem isso, não existe release.

## Estrutura

```text
src/main/kotlin/       domínio executável
src/test/kotlin/       testes de risco
db/migrations/         controles relacionais
docs/                   arquitetura, decisões, políticas e runbooks
governance/             autoria, controles, revisão e procedência
tools/                  validação, testes, build e verificação
evidence/               resultado reproduzível da execução
build/                  artefato compilado
```

## Assinatura

A assinatura criptográfica não está embutida.
Ela precisa ser produzida com a chave real do responsável e validada fora deste ZIP.
Assinatura inventada não protege autoria.
Só cria prova contra quem publicou.
