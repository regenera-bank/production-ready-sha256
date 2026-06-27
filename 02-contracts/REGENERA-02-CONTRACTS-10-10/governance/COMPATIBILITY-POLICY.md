# Compatibilidade

**Documento:** CONTRACT-COMPAT-001

## Compatível

- adicionar campo opcional;
- adicionar resposta nova sem alterar as existentes;
- adicionar enum somente quando consumidores toleram valor desconhecido;
- adicionar evento novo em canal novo.

## Incompatível

- remover path, operação, evento ou campo;
- tornar campo opcional obrigatório;
- reduzir limite aceito;
- alterar tipo;
- renomear código de erro;
- mudar unidade monetária;
- retirar `UNKNOWN` de fluxo assíncrono;
- reutilizar evento antigo com significado novo.

Compatibilidade não é opinião do produtor.
É prova contra consumidores reais.
