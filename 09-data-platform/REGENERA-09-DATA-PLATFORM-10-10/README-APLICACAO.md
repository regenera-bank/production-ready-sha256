# Aplicação do pacote

Este diretório é autocontido. Não instala dependências e não executa código remoto.

## Validação completa

```bash
make all
```

## Resultado esperado

- validação estrutural aprovada;
- testes comportamentais aprovados;
- scan de segurança aprovado;
- release interna montada em `dist/`;
- manifesto, SBOM, proveniência e checksums íntegros.

## Ativação produtiva

A ativação exige catálogo institucional, IAM, secret manager, storage imutável, mensageria, ambiente de execução, owner real, aprovador independente, política de retenção aprovada, base legal validada e assinatura criptográfica externa.

Sem isso, existe software validado.
Não existe plataforma produtiva autorizada.
