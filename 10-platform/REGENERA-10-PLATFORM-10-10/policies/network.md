# Rede

**Documento:** PLAT-POL-NET-001  
**Estado:** obrigatório  
**Owner:** Platform Engineering  
**Aprovador:** autoridade independente  
**Revisão:** trimestral

## Objetivo

Controlar segmentação, default deny, egress, mTLS, borda e evidência.

## Escopo

Aplica-se a ambientes, pipelines, workloads e dados administrados pela plataforma.

## Controles obrigatórios

- toda mudança possui owner, ticket, evidência e aprovação segregada;
- toda credencial é temporária ou mantida em cofre institucional;
- todo artefato é imutável, identificado por digest e acompanhado de SBOM;
- toda exceção possui prazo, aprovador independente e plano de retirada;
- todo controle crítico falha fechado quando a evidência não existe;
- toda ativação externa depende de prova do ambiente real.

## Evidências

Manifesto, checksums, assinatura, logs de pipeline, ticket, resultado de teste e registro de aprovação.

## Exceções

Validade máxima de 24 horas para risco crítico. Autoaprovação é proibida. Exceção vencida bloqueia a operação.

## Métricas

A fonte, a janela, o limite e a ação estão definidos em `config/platform-baseline.json`.

## Violações

Violação crítica interrompe promoção. Não existe waiver silencioso.
