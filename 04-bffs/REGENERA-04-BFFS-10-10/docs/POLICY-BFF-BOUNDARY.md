# Política de fronteira dos BFFs

**Documento:** BFF-POL-001  
**Revisão:** anual ou após incidente material  
**Owner:** BFF Platform Engineering  
**Aprovador:** Change Authority

## Escopo

Aplica-se a Web, Mobile, Operations, Partner API e Open Finance API.

## Controles obrigatórios

1. BFF não acessa banco de dados do core.
2. BFF não cria lançamento contábil.
3. BFF não calcula saldo autoritativo.
4. Comando mutável exige idempotência e correlação.
5. Timeout ambíguo vira `UNKNOWN`.
6. Resposta financeira usa `no-store` quando exposta por HTTP.
7. Dados retornados seguem minimização por canal.
8. Segredo não entra em log, evento ou corpo de resposta.

## Evidência

- resultado de testes;
- matriz de controles;
- manifesto e checksums;
- revisão independente;
- aprovação de release.

## Exceção

Exceção exige autoridade independente, validade máxima de 24 horas e retrospectiva. Não existe exceção para duplicidade financeira, segregação ou segredo exposto.

## Violação

Violação bloqueia release. Em produção, abre incidente e exige avaliação de impacto financeiro e de dados.
