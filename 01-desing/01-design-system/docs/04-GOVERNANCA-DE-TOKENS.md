# Governança de tokens

**Documento:** DS-TOK-001

## Regra

Token descreve decisão compartilhada.
Valor isolado continua sendo detalhe local.

## Nome

O nome expressa intenção:

- `color.text.primary`;
- `color.state.danger`;
- `spacing.4`;
- `accessibility.minimumTouchTarget`.

Nome de cor crua não atravessa contrato de componente.
`blue500` não explica responsabilidade.

## Alteração

Toda mudança registra:

- motivo;
- consumidores;
- diferença visual;
- impacto de contraste;
- impacto por plataforma;
- estratégia de migração;
- rollback.

## Paridade

Cada token publicado deve aparecer nas quatro saídas suportadas ou ser marcado como exclusivo com justificativa.

Nesta release não existem exclusivos.

## Remoção

Token não some em silêncio.
Primeiro depreca.
Depois mede.
Só então remove.
