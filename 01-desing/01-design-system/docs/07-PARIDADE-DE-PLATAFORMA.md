# Paridade de plataforma

**Documento:** DS-PAR-001

## Objetivo

A mesma intenção precisa sobreviver a quatro toolchains.
Não precisa parecer pixel por pixel.
Precisa continuar sendo a mesma decisão.

## Contrato comum

- nomes semânticos;
- cores;
- espaçamento;
- tipografia;
- raio;
- movimento;
- alvos de toque;
- estados financeiros.

## Diferença permitida

A plataforma pode adaptar:

- unidade;
- API nativa;
- comportamento de foco;
- dinâmica de fonte;
- convenção de recurso.

Não pode adaptar por conta própria:

- significado de estado;
- contraste mínimo;
- texto de risco;
- regra de repetição em estado desconhecido.

## Prova

O build grava hash da fonte e lista de saídas.
Os testes confirmam presença dos tokens em cada plataforma.
