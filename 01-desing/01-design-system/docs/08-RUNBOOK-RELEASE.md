# Runbook de release

**Documento:** DS-RUN-REL-001

## Severidade

| Nível | Condição | Resposta |
|---|---|---|
| SEV1 | estado financeiro induz ação errada ou bloqueia operação crítica | interromper promoção e reverter |
| SEV2 | acessibilidade crítica ou paridade quebrada | bloquear promoção |
| SEV3 | regressão visual sem perda funcional | corrigir antes da próxima janela |

## Pré-condições

- branch protegida;
- owner presente;
- revisão independente;
- assinatura disponível;
- `npm ci --ignore-scripts` concluído;
- `npm run all` com exit code zero.

## Avançar

Avance somente quando:

1. manifesto fecha;
2. checksums fecham;
3. quatro plataformas foram geradas;
4. testes passam;
5. segurança passa;
6. versão anterior está preservada;
7. aprovador independente assinou.

## Abortar

Abortar diante de:

- hash divergente;
- saída ausente;
- contraste abaixo do mínimo;
- componente sem foco;
- estado `unknown` com repetição direta;
- dependência externa não aprovada;
- evidência incompleta.

## Rollback

1. congelar promoção;
2. identificar hash anterior;
3. restaurar pacote completo;
4. limpar cache de assets;
5. validar tokens ativos;
6. executar smoke test dos estados financeiros;
7. comunicar consumidores;
8. abrir análise de causa.

## Evidência

Preservar comandos, exit codes, hashes, identidade do executor, identidade do aprovador e horário.

## Encerramento

Encerrar quando consumidores confirmarem a versão anterior e nenhum estado estiver ambíguo.
