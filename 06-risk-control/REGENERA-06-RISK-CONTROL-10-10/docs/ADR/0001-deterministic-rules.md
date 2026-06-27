# ADR-001 — regras determinísticas antes de modelo opaco

## Contexto

Decisão de risco precisa ser explicada depois.
Pontuação sem motivo não sustenta bloqueio nem defesa.

## Alternativas

1. regras determinísticas versionadas;
2. modelo estatístico como única decisão;
3. decisão manual integral;
4. modelo com regras de contenção.

## Decisão

A baseline usa regras determinísticas.
Modelo futuro só entra com versionamento, dados aprovados, validação, drift,
explicabilidade e fallback seguro.

## Consequência

Cobertura menor no início.
Explicação maior desde o primeiro incidente.
