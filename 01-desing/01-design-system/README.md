# Regenera Design System

**Documento:** DS-ROOT-001  
**Versão:** 1.0.0  
**Responsável técnico declarado:** Don Paulo Ricardo  
**Estado técnico:** verificado  
**Aprovação institucional:** pendente de assinatura criptográfica e revisão independente

Este repositório concentra tokens, contratos de componente e saídas para Web, Android, iOS e Windows.

Não calcula saldo.
Não autoriza transação.
Não decide fraude.
Não inventa estado financeiro.

Design system orienta interface.
A verdade continua no domínio.

## Estrutura

- `tokens/`: fonte canônica;
- `packages/web/`: núcleo Web sem dependência externa em runtime;
- `dist/`: saídas determinísticas por plataforma;
- `governance/`: controles, owners e critérios de promoção;
- `docs/`: arquitetura, acessibilidade, release e runbooks;
- `tests/`: testes de contrato, paridade, segurança e governança;
- `evidence/`: prova regenerável da release.

## Execução

```sh
npm ci --ignore-scripts
npm run all
```

O comando limpa a saída anterior, valida a árvore, reconstrói os artefatos, executa os testes, verifica segurança, gera evidência e fecha os hashes.

## Regra de publicação

A release técnica pode ser reproduzida localmente.
A adoção institucional exige revisão independente e assinatura real do titular.

Assinatura não se simula.
Aprovação sem chave é só texto.
