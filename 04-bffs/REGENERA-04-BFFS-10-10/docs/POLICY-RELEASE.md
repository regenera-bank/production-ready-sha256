# Política de release dos BFFs

**Documento:** BFF-POL-002  
**Owner:** Release Engineering  
**Aprovador:** Change Authority

## Entrada obrigatória

- pull request revisado;
- testes com falha zero;
- validação estrutural;
- security scan;
- manifesto;
- checksums;
- SBOM;
- rollback documentado;
- assinatura externa real.

## Bloqueios

- autor aprovando a própria mudança;
- owner sem vínculo corporativo;
- evidência ausente;
- exceção vencida;
- hash divergente;
- dependência externa não homologada;
- estado financeiro desconhecido sem runbook.

## Promoção

A promoção entre ambientes é feita por identidade de serviço segregada. Credencial pessoal não promove release.

## Retenção

Manifesto, hashes, aprovação, logs de gate e assinatura permanecem conforme a política institucional de retenção. O prazo final depende de validação jurídica.
