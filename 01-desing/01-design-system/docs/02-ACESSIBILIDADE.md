# Acessibilidade

**Documento:** DS-ACC-001  
**Owner:** Don Paulo Ricardo  
**Revisor independente exigido:** Accessibility Reviewer

## Critérios bloqueantes

- texto normal: contraste mínimo 4,5:1;
- texto grande: contraste mínimo 3:1;
- alvo de toque: mínimo 44 por 44;
- foco: visível e não dependente de cor;
- erro: texto, semântica e relação com o campo;
- movimento: alternativa reduzida;
- estado: anunciado por tecnologia assistiva;
- ordem: leitura coerente sem CSS.

## Conteúdo financeiro

Valor, moeda e sinal permanecem visíveis.
Cor negativa ajuda.
Não decide sozinha.

Comprovante preserva identificador, data e estado.
Mascaramento não pode apagar o dado necessário para conferência.

## Teclado

Todo controle interativo deve ser alcançável, operável e encerrável por teclado.
Modal sem retorno de foco é armadilha.

## Teste

A release exige:

1. validação automática de tokens;
2. navegação por teclado;
3. leitura de nome, papel e estado;
4. zoom a 200%;
5. redução de movimento;
6. revisão humana independente.

Automação encontra regressão conhecida.
Pessoa encontra interface que cansou de fingir que é clara.
