# ADR 0002 — Núcleo Web sem framework

**Estado:** aceito  
**Data:** 2026-06-26  
**Responsável:** Don Paulo Ricardo

## Contexto

Componentes básicos precisam sobreviver a mudanças do canal Web.

## Alternativas

1. acoplar o núcleo a um framework;
2. publicar apenas CSS;
3. publicar contratos e renderizadores sem dependência externa;
4. manter cópias por aplicação.

## Decisão

Publicar núcleo ESM com HTML semântico e CSS versionado.
Adaptadores específicos podem existir fora desta fronteira.

## Consequências

O contrato fica testável sem instalar ecossistema inteiro.
Integração com framework continua responsabilidade do canal.

## Risco

Renderização por string exige escape obrigatório.
O núcleo centraliza essa função e os testes tentam quebrá-la.

## Rollback

Consumidores fixam a versão anterior do pacote.
