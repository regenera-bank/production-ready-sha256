# Política de release e promoção

**Documento:** POL-REL-001  
**Estado:** controlled  
**Autor responsável:** Don Paulo Ricardo  
**Owner operacional:** engineering-governance  
**Vigência:** 2026-06-26  
**Próxima revisão:** 2026-12-23  
**Ciclo máximo:** 180 dias


## Escopo

Artefatos, documentos, automações e configurações promovidos entre ambientes controlados.

## Responsabilidades

Release Engineering empacota. O autor responde pela mudança. Segurança e Operações revisam risco. A Change Authority libera promoção.

## Evidências

Manifesto, checksums, SBOM, resultados, aprovações, assinatura, janela, rollback e validação pós-release.

## Objetivo

Garantir que o artefato promovido seja exatamente o artefato testado, aprovado e assinado.

## Classes de mudança

| Classe | Exemplo | Aprovações mínimas |
|---|---|---|
| R1 | documentação sem controle | owner do documento |
| R2 | política, automação ou controle | owner + revisão independente |
| R3 | impacto financeiro, segurança ou disponibilidade | owner + segurança + operações + change authority |
| R4 | emergência | incident commander + change authority; retrospectiva em 24h |

## Gate obrigatório

A release para quando qualquer item abaixo falha:

- validação estrutural;
- testes comportamentais;
- varredura de segredo;
- manifesto e hashes;
- SBOM;
- aprovação independente;
- plano de rollback;
- evidência de restauração;
- assinatura criptográfica no repositório fonte.

## Integridade

O hash do ZIP é externo ao ZIP. O payload possui manifesto próprio. Evidência gerada antes da árvore final é descartada.

## Promoção

O autor não promove sozinho. A autoridade de mudança confere versão, hash, aprovação, janela, impacto e retorno.

## Emergência

Mudança emergencial não reduz a obrigação de prova. Adia apenas a revisão completa, limitada a 24 horas.

## Retenção

Manifesto, assinatura, aprovações, resultados e rollback são mantidos por cinco anos, salvo prazo superior definido por obrigação aplicável.

## Métricas

- releases sem rollback validado: 0;
- divergência entre artefato testado e publicado: 0;
- tempo-alvo de rollback: 15 minutos;
- autoaprovação: 0.
