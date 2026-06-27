# Aplicação controlada do pacote de integrações

Este diretório não deve ser copiado por cima de uma árvore ativa sem revisão de diff.

## Verificação local

```bash
make all
```

## Promoção

1. validar o ZIP e o `.sha256`;
2. verificar a assinatura `.asc` real;
3. abrir pull request para o repositório canônico `07-integrations`;
4. comparar o registro de adaptadores com contratos e homologações vigentes;
5. manter todos os adaptadores externos bloqueados até anexar evidência institucional;
6. promover somente após aprovação independente.

O pacote não carrega segredo, certificado nem credencial de fornecedor.
