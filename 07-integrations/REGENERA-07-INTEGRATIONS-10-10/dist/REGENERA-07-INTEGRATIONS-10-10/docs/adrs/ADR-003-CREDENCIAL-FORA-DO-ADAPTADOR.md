# ADR-003 — Credencial fora do adaptador

## Contexto

Código de integração é revisado, copiado e empacotado.
Segredo dentro dele viaja junto.

## Decisão

Adaptadores recebem referências efêmeras de credencial em runtime.
Chaves privadas, tokens e certificados não entram na release.

## Consequências

- secret manager obrigatório;
- rotação sem rebuild;
- testes usam material local descartável;
- ativação depende de integração institucional de segredos.
