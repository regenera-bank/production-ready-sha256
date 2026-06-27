# Arquitetura

**Documento:** DS-ARC-001

## Fronteira

O design system publica linguagem visual e contratos de interação.
Não publica regra financeira.
Não consulta banco.
Não liquida operação.

## Fonte de verdade

`tokens/` é a origem.
`dist/` é consequência.

Editar arquivo gerado é perder a próxima disputa para o build.

## Camadas

1. tokens primitivos;
2. tokens semânticos;
3. contratos de componente;
4. adaptadores de plataforma;
5. documentação;
6. evidência de release.

## Plataformas

- Web recebe CSS variables e JSON;
- Android recebe resources XML;
- iOS recebe constantes Swift;
- Windows recebe ResourceDictionary XAML.

Todos nascem do mesmo conjunto.
Diferença local precisa ser explícita, não acidental.

## Estado financeiro

A interface representa o estado recebido.

`unknown` não significa falha.
`processing` não significa sucesso.
`settled` não significa reconciliado.

O componente não promove estado por conta própria.

## Dependências

O núcleo Web usa recursos nativos da plataforma.
Não depende de CDN.
Não carrega fonte remota.
Não executa script de terceiro.

## Falha

Ausência de token, saída divergente ou estado desconhecido bloqueia a release.
Fallback silencioso só esconde a causa.
