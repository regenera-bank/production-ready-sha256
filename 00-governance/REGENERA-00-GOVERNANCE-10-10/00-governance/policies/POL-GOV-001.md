# Política de governança documental

**Documento:** POL-GOV-001  
**Estado:** controlled  
**Autor responsável:** Don Paulo Ricardo  
**Owner operacional:** governance-corporate  
**Vigência:** 2026-06-26  
**Próxima revisão:** 2027-06-26  
**Ciclo máximo:** 365 dias


## Objetivo

Impedir que documento sem responsável, revisão ou prova seja tratado como controle vigente.

## Escopo

Aplica-se a políticas, padrões, ADRs, runbooks, matrizes, evidências e registros de aprovação desta árvore.

## Responsabilidades

| Papel | Responsabilidade |
|---|---|
| Autor | Propõe conteúdo e mantém a justificativa |
| Owner | Garante execução e revisão periódica |
| Revisor | Questiona premissas, evidência e impacto |
| Aprovador | Assume o risco residual e não pode ser o autor |
| Auditor | Verifica trilha, integridade e eficácia |

## Controles obrigatórios

1. Todo documento controlado possui `document_id` único.
2. Vigência e próxima revisão são datas verificáveis.
3. Owner existe no `OWNERS.yaml` e está ativo.
4. Aprovação independente é obrigatória para política, release e exceção crítica.
5. Alteração material exige histórico, motivo, diff e evidência.
6. Documento vencido entra em não conformidade até revisão formal.

## Exceções

Exceção possui owner, justificativa, risco, compensação, expiração e autoridade de aceite. Prazo aberto não é aceito.

## Evidências

Registro documental, diff, aprovação, hash e resultado de validação.

## Métricas

- documentos vencidos: alvo 0;
- documentos sem owner: alvo 0;
- autoaprovações: tolerância 0;
- revisão concluída no prazo: alvo 100%.

## Violações

Documento inválido não é removido. É marcado como ineficaz, bloqueado para uso e encaminhado ao owner.
