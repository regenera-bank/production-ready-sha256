# Assinatura de commits e release

A assinatura deve usar chave controlada pelo titular.
Este pacote não contém chave privada.

## Requisitos

- identidade Git confirmada;
- assinatura de commit habilitada;
- chave pública publicada no repositório corporativo;
- tag de release assinada;
- hash do ZIP registrado no ticket de mudança;
- verificação independente antes da promoção.

## Verificação

```sh
git verify-commit HEAD
git verify-tag DS-2026-001
shasum -a 256 REGENERA-01-DESIGN-SYSTEM-10-10.zip
```

Assinatura copiada é fraude.
Assinatura pendente fica pendente.
