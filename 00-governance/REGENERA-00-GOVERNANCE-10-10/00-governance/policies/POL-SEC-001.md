# Política de segurança cibernética e segredo

**Documento:** POL-SEC-001  
**Estado:** controlled  
**Autor responsável:** Don Paulo Ricardo  
**Owner operacional:** security-governance  
**Vigência:** 2026-06-26  
**Próxima revisão:** 2026-12-23  
**Ciclo máximo:** 180 dias


## Objetivo

Proteger confidencialidade, integridade e disponibilidade sem perder a prova do que aconteceu.

## Responsabilidades

O CISO responde pela política. Security Engineering executa. Owners corrigem. Operações contém. Auditoria verifica eficácia.

## Evidências

Scans, tickets, concessões, rotações, timelines, hashes, relatórios de incidente e revisão de acesso.

## Escopo

Código, automação, infraestrutura, estações administrativas, pipelines, terceiros e evidências.

## Regras

1. Segredo não entra em fonte, log, imagem, artefato ou evidência.
2. Credencial privilegiada é individual, temporária e revogável.
3. Chave privada não é distribuída no pacote.
4. Incidente preserva evidência antes da limpeza.
5. Terceiro recebe o menor acesso pelo menor tempo.
6. Material sensível usa canal e repositório aprovados.

## Detecção

Varredura por commit, por release e em repositório completo. Achado de alta confiança bloqueia promoção.

## Resposta

Revogar, rotacionar, delimitar exposição, preservar trilha, notificar autoridade interna e acompanhar efeito residual.

## Métricas

- segredo em código: 0;
- credencial crítica fora do prazo: 0;
- patch crítico: até 72 horas;
- revisão de acesso crítico: 30 dias.
