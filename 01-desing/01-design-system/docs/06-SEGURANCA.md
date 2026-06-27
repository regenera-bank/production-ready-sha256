# Segurança

**Documento:** DS-SEC-001

## Princípios

- nenhuma chave no repositório;
- nenhuma dependência remota em runtime;
- nenhuma execução dinâmica de texto;
- nenhum dado financeiro em exemplo de interface;
- nenhum asset sem procedência;
- nenhuma permissão de escrita no workflow de verificação.

## Cadeia de suprimento

A release mantém inventário de dependências e hashes.
Dependência sem versão controlada não entra.

Este pacote não possui dependência de runtime externa.

## Conteúdo sensível

Componente recebe o mínimo necessário.
Log de interface não recebe token, chave Pix integral, documento integral ou payload financeiro bruto.

## Vulnerabilidade

Achado crítico bloqueia promoção.
Achado alto exige correção ou aceite formal com prazo.
Aceite sem compensação é adiamento com nome bonito.

## Revisão

- por mudança de dependência;
- por release;
- após incidente;
- no mínimo trimestral.
