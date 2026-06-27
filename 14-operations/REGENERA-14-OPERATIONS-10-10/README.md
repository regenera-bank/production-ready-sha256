# Regenera Bank — Operations

Pacote técnico do domínio de operações bancárias.

A release concentra controles executáveis para incidentes, mudanças, filas operacionais, reconciliação, continuidade, passagem de turno, runbooks, suporte e aprovações. A estrutura anterior foi inventariada em `evidence/source/SOURCE-INVENTORY.json` e não foi promovida como prova de maturidade.

## Comandos

```bash
make all
```

O comando executa validação estrutural, testes, análise de segurança, build de evidências, verificação de integridade e limpeza de resíduos de runtime.

## Escopo comprovado

A aprovação produzida por este pacote vale somente para o escopo técnico local. Integrações com IAM, SIEM, ITSM, observabilidade, mensageria, bancos, provedores financeiros e ambiente de continuidade exigem evidência externa real.

## Princípios

- falha ambígua não autoriza repetição;
- operação privilegiada exige MFA e segregação;
- mudança não fecha sem verificação independente;
- incidente crítico não fecha sem reconciliação e revisão;
- fila não aceita efeito duplicado;
- evidência é vinculada por SHA-256;
- continuidade é medida, não declarada.
