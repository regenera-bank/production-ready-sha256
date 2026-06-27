# Arquitetura

O pacote separa quatro camadas:

1. regras de domínio de qualidade em `src/`;
2. testes de comportamento em `tests/`;
3. políticas e contratos em `config/` e `contracts/`;
4. ferramentas de evidência e release em `tools/`.

A árvore ativa não depende de serviços externos para executar. Dependências externas são bloqueios de ativação, não resultados simulados.
