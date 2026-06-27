# Política de integridade financeira

**Documento:** POL-CORE-001  
**Owner declarado:** Don Paulo Ricardo  
**Revisão:** anual ou após incidente financeiro material

## Objetivo

Impedir alteração financeira sem causa, prova e reversibilidade contábil.

## Escopo

Aplica-se a contas, ledger, pagamentos, Pix, tarifas, limites, reservas, reconciliação e relatórios financeiros.

## Controles obrigatórios

1. dinheiro usa unidade mínima inteira;
2. lançamento tem no mínimo duas linhas;
3. débitos e créditos fecham no mesmo lançamento;
4. moeda não se mistura dentro do lançamento;
5. lançamento postado não sofre update ou delete;
6. reversão cria novo lançamento compensatório;
7. saldo deriva do razão;
8. operação mutável exige idempotência durável;
9. efeito financeiro e outbox pertencem à mesma transação;
10. estado incerto vira `UNKNOWN`;
11. `UNKNOWN` bloqueia repetição automática;
12. reconciliação registra evidência e responsável.

## Aprovação

Mudança em qualquer controle exige revisão de Core Banking, Segurança, Operações e autoridade de mudança.
O autor não aprova sozinho alteração que modifica risco financeiro.

## Exceção

Exceção precisa de:

- risco descrito;
- escopo limitado;
- prazo de validade;
- compensação;
- aprovador independente;
- ticket e evidência.

Exceção vencida bloqueia release.

## Evidência

- resultados de testes;
- migration revisada;
- diff aprovado;
- manifesto;
- assinatura;
- reconciliação sem quebra;
- rollback ou plano compensatório.

## Violação

Violação material suspende promoção e abre incidente.
Não existe waiver retroativo para efeito financeiro já produzido.
