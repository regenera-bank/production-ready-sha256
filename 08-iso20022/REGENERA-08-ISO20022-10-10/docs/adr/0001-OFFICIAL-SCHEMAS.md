# ADR 0001 — XSD oficial permanece externo até procedência comprovada

## Contexto
O pacote original não continha XSD.

## Alternativas
1. inventar schemas mínimos;
2. baixar artefatos sem registrar fonte;
3. manter perfil interno e bloquear conformidade externa.

## Decisão
Alternativa 3.

## Razão
Schema sem procedência muda o significado da mensagem e ainda parece oficial.
Isso é pior que falhar cedo.

## Consequência
Os testes locais são válidos para a implementação interna.
A homologação externa continua bloqueada.

## Revisão
Reabrir quando os XSDs aplicáveis estiverem versionados, licenciados, hashados e aprovados.
