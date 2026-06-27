# ADR 0001 — Fonte única de tokens

**Estado:** aceito  
**Data:** 2026-06-26  
**Responsável:** Don Paulo Ricardo

## Contexto

Valores visuais duplicados entre plataformas divergiam sem alarme.

## Alternativas

1. cada plataforma mantém seus valores;
2. copiar JSON manualmente;
3. fonte canônica com geração determinística;
4. serviço remoto de tokens em runtime.

## Decisão

Adotar fonte canônica local e gerar saídas no build.

## Rejeições

A primeira alternativa institucionaliza divergência.
A segunda depende de disciplina manual.
A quarta transforma cor e espaçamento em dependência de rede.

## Riscos aceitos

O gerador vira componente crítico da release.
Por isso possui testes de paridade e reprodutibilidade.

## Migração

Consumidores adotam saídas versionadas.
Valores locais são removidos depois de inventário e comparação.

## Rollback

Restaurar fonte e saídas do hash anterior.

## Revisão

Revisar após inclusão de nova plataforma ou mudança de formato.
