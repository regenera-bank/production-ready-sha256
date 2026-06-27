# Modelo de ameaças

## Ameaças

- teste verde sem verificar risco;
- evidência alterada após aprovação;
- segredo incorporado no repositório;
- workflow com permissão excessiva;
- ação de pipeline não fixada por digest;
- replay idempotente com payload divergente;
- cobertura alta com mutantes críticos sobreviventes;
- carga pequena usada como prova de capacidade;
- experimento destrutivo sem condição de aborto;
- dados reais usados em teste.

## Controles

Gates falham fechados, evidência recebe SHA-256, dados são sintéticos, experimentos exigem segregação e a release final é reconstruída em diretório limpo.
