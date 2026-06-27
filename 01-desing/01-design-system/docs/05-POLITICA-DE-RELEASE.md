# Política de release

**Documento:** DS-REL-001  
**Owner:** Don Paulo Ricardo  
**Aprovador:** Change Authority independente  
**Retenção da evidência:** cinco anos, sujeita à validação jurídica

## Escopo

Aplica-se a tokens, componentes, assets, saídas geradas e documentação normativa do design system.

## Classes

- patch: correção sem quebra de contrato;
- minor: capacidade compatível;
- major: quebra de contrato, semântica ou acessibilidade.

## Evidência obrigatória

- diff revisado;
- testes aprovados;
- build reproduzível;
- manifesto;
- checksums;
- inventário de dependências;
- relatório de segurança;
- aprovação independente;
- assinatura criptográfica;
- rollback.

## Bloqueios

A release falha quando:

- autor e aprovador são a mesma identidade;
- assinatura não é verificável;
- owner não existe;
- controle bloqueante falha;
- evidência está ausente;
- exceção expirou;
- build repetido diverge;
- asset remoto aparece em runtime.

## Emergência

Mudança emergencial não elimina controle.
Reduz janela e aumenta revisão posterior.

Exige:

- incidente associado;
- autoridade executiva e segurança;
- validade máxima de 24 horas;
- revisão retrospectiva em um dia útil;
- correção definitiva ou reversão.

## Promoção

Ambiente posterior recebe o mesmo hash aprovado.
Reconstruir entre ambientes cria outra release.

## Rollback

Meta: 15 minutos para retornar à versão anterior dos artefatos.
Rollback restaura artefato completo.
Misturar tokens de versões diferentes cria um sistema que ninguém testou.
