# Regenera Bank — Documentação Canônica

Este pacote é a autoridade documental do workspace Regenera Bank. Ele não prova operação de infraestrutura, homologação regulatória ou aprovação institucional. Ele prova apenas a consistência, o versionamento, a rastreabilidade e a integridade da documentação incluída nesta release.

## Comandos

```bash
make validate
make test
make security
make build
make evidence
make verify-release
make all
```

## Regras centrais

- um documento ativo possui identificador, owner, versão, classificação e prazo de revisão;
- afirmação operacional exige evidência externa identificável;
- protocolo, homologação, assinatura e aceite nunca são inferidos;
- documento substituído permanece rastreável, mas não é fonte de verdade;
- links quebrados, IDs duplicados, revisão vencida e segredo incorporado bloqueiam a release;
- o hash externo do ZIP cobre payload e evidências; manifestos internos não tentam assinar a si próprios.

A entrada de navegação está em [`docs/index.md`](docs/index.md).
