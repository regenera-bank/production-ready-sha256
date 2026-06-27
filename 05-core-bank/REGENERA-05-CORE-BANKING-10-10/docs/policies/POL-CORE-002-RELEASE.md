# Política de release do core bancário

**Documento:** POL-CORE-002  
**Owner declarado:** Don Paulo Ricardo  
**Revisão:** semestral

## Regra

Release só existe quando o artefato recebido corresponde à evidência arquivada.

## Gates

Toda release precisa comprovar:

- árvore limpa;
- testes aprovados;
- validação estrutural;
- secret scan;
- artefato reproduzível;
- manifesto completo;
- checksums íntegros;
- SBOM;
- proveniência;
- aprovação segregada;
- assinatura criptográfica;
- plano de rollback ou compensação;
- compatibilidade de migration.

## Bloqueios

A release falha quando:

- arquivo não está no manifesto;
- hash diverge;
- owner não existe;
- aprovação vem do próprio autor;
- assinatura está ausente;
- exceção venceu;
- teste foi omitido;
- evidência foi produzida antes da árvore final;
- migration destrutiva não possui plano de transição.

## Emergência

Release emergencial reduz prazo.
Não reduz prova.

Precisa de:

- incidente associado;
- aprovador de plantão;
- escopo mínimo;
- rollback imediato;
- revisão retrospectiva em até 24 horas.
