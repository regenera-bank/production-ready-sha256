# Regenera Bank — aplicação do pacote de governança

Este pacote contém a camada de governança técnica do Regenera Bank.

A árvore foi construída para ser validada offline. Nenhum comando instala dependência, acessa rede ou altera o repositório de destino sem ação explícita do operador.

## Verificação local

```bash
cd 00-governance
make clean
make validate
make test
make security
make continuity
make build
make verify-release
```

## Aplicação

A aplicação no repositório canônico exige cópia controlada, backup do destino e revisão do diff. O pacote não executa deploy e não promove ambiente.

A assinatura criptográfica da release deve ser feita no ambiente do responsável, usando a chave real de Don Paulo Ricardo. O pacote não contém chave privada e não fabrica assinatura.
