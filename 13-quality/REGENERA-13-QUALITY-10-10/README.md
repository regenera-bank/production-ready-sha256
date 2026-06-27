# Regenera Bank — Quality

Pacote de qualidade executável para sistemas financeiros.

A release concentra regras, gates e evidências que podem ser comprovados localmente. Não declara infraestrutura, homologação ou aprovação externa sem documento assinado.

## Execução

```bash
make all
```

O comando limpa artefatos transitórios, valida a estrutura, executa testes, verifica segurança, gera a release interna e confirma os checksums.

## Escopo ativo

- contratos e compatibilidade;
- invariantes financeiras;
- idempotência e estado desconhecido;
- qualidade de testes e mutação;
- desempenho e SLO;
- resiliência e experimentos controlados;
- segurança de pipeline;
- acessibilidade básica de interfaces;
- dados sintéticos;
- evidência e gates de release.

## Limites

Testes externos de carga, dispositivos reais, pentest independente, homologação regulatória e exercício de continuidade exigem ambiente, credenciais e aprovação institucional. Permanecem bloqueados até evidência real.
