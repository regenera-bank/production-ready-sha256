# ADR-001 — BFF por canal

## Contexto

Web, Mobile, Operations, Partners e Open Finance carregam riscos diferentes. Uma API única transforma conveniência em acoplamento.

## Alternativas

- API única para todos os canais;
- GraphQL central sem fronteira por canal;
- BFF por canal com shared kernel restrito;
- acesso direto do canal aos serviços de domínio.

## Decisão

BFF por canal. Shared kernel contém apenas controles comuns e tipos de fronteira.

## Razões

- reduz privilégio;
- separa autenticação e rate limit;
- evita resposta com dado que o canal não deveria receber;
- permite evolução independente sem duplicar regra financeira.

## Risco aceito

Mais serviços e mais observabilidade. Complexidade explícita custa menos que privilégio implícito.

## Rollback

Não existe rollback para API única sem reabrir análise de ameaça. Migração ocorre rota por rota, com compatibilidade contratual e tráfego controlado.
