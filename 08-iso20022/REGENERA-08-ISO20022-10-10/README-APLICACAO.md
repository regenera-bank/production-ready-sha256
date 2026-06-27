# Aplicação do pacote

Este pacote substitui a estrutura ativa de `08-iso20022` somente depois de validação local e backup.

## Pré-condições

- Python 3.11 ou superior;
- `make`;
- repositório de destino identificado;
- revisão humana do diff;
- assinatura externa da distribuição;
- XSD oficial incorporado antes de homologação externa.

## Validação

```sh
make all
```

## Aplicação

A aplicação no repositório canônico deve ocorrer por cópia controlada, com backup,
comparação de SHA-256 e revisão do diff. O pacote não contém comando destrutivo.

## Bloqueio externo

A validação semântica local não substitui homologação com infraestrutura, parceiro,
certificado, assinatura XML ou schema oficial. Sem essa prova, a ativação externa permanece bloqueada.
