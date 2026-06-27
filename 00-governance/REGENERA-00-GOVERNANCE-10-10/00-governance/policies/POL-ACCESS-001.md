# Política de acesso privilegiado

**Documento:** POL-ACCESS-001  
**Estado:** controlled  
**Autor responsável:** Don Paulo Ricardo  
**Owner operacional:** security-governance  
**Vigência:** 2026-06-26  
**Próxima revisão:** 2026-12-23  
**Ciclo máximo:** 180 dias


## Objetivo

Reduzir o tempo e o alcance de privilégios administrativos.

## Escopo

Ambientes, pipelines, cofres, bancos, consoles, estações administrativas e acessos de terceiros.

## Responsabilidades

Security Engineering concede e revoga. O owner do sistema justifica. O CISO responde pelo controle. Auditoria verifica a trilha.

## Métricas

- acessos sem expiração: 0;
- contas compartilhadas: 0;
- revogação fora do prazo: 0;

## Princípios

Acesso privilegiado é exceção operacional, não identidade permanente.

## Concessão

Pedido informa sistema, ação, motivo, janela, ticket e aprovador. MFA é obrigatório. Conta compartilhada é proibida.

## Elevação

A elevação expira automaticamente. Sessão administrativa crítica deve ser registrada quando a plataforma suportar.

## Contas de emergência

Uso exige incidente declarado, dupla custódia e revisão em até 24 horas.

## Terceiros

Acesso de fornecedor possui sponsor interno, escopo reduzido, validade e revogação no encerramento contratual.

## Revisão

Acessos críticos são revisados a cada 30 dias. Desligamento ou mudança de função inicia revogação imediata.

## Evidências

Pedido, aprovação, concessão, autenticação, comandos relevantes, expiração e revisão.
