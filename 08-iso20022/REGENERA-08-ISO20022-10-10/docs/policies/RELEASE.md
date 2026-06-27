# Release de contratos ISO 20022

## Objetivo
Impedir que uma mensagem ambígua, não autorizada ou sem prova seja tratada como instrução válida.

## Escopo
Aplica-se a código, perfis, políticas, testes, evidência e distribuição.

## Responsabilidades
- `payments-engineering`: implementação e correção;
- `payments-architecture`: perfil, versão e compatibilidade;
- `engineering-security`: parser, certificado e assinatura;
- `reconciliation`: estado incerto e divergência;
- `release-engineering`: manifesto, hashes e distribuição;
- `change-authority`: aprovação independente.

## Controles obrigatórios
- owner e versão identificados;
- validação sintática e semântica;
- idempotência e digest;
- trilha de decisão;
- evidência do teste;
- revisão segregada;
- assinatura externa antes da ativação;
- rollback ou bloqueio documentado.

## Critérios de bloqueio
A release falha com teste vermelho, segredo, XSD sem procedência, autoaprovação,
assinatura ausente, exceção vencida ou evidência divergente.

## Exceções
Seguem `governance/EXCEPTION-PROCESS.md`.
Exceção expira. Exceção sem medida compensatória não existe.

## Evidência
- `evidence/generated/VALIDATION-RESULTS.json`;
- `evidence/generated/TEST-RESULTS.json`;
- `evidence/generated/SECURITY-RESULTS.json`;
- `PACKAGE-CHECKSUMS.sha256`;
- registro de aprovação assinado.

## Métricas
- mensagens rejeitadas por código;
- mensagens em `UNKNOWN`;
- tempo de reconciliação;
- divergências por perfil;
- releases bloqueadas;
- exceções abertas e vencidas.

## Revisão
Trimestral e sempre que versão, parceiro, certificado ou regra de liquidação mudar.
