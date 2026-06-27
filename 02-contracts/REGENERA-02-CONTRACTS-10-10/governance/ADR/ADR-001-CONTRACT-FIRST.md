# ADR-001 — contrato antes do código

**Estado:** aceito  
**Responsável declarado:** Don Paulo Ricardo

## Contexto

Canais, BFFs e serviços evoluem em ritmos diferentes.
Acoplamento por implementação transforma release em negociação de emergência.

## Alternativas

1. documentação depois do código;
2. tipos compartilhados dentro de um monorepo;
3. contratos versionados, independentes e testados;
4. integração direta por banco de dados.

## Decisão

Contratos versionados são a fronteira oficial.
Banco de dados não é API.
Tipo interno não é compromisso externo.

## Consequências

- mudança passa por compatibilidade;
- SDK é derivado, nunca fonte;
- produtor e consumidor validam o mesmo contrato;
- ruptura exige versão principal e plano de migração.

## Rollback

Publicação incompatível não é corrigida editando a versão publicada.
Restaura-se a versão anterior e abre-se uma nova versão.
Histórico não some para facilitar release.
