# Arquitetura

A fronteira tem quatro passos:

```text
bytes recebidos
  -> parser seguro
  -> perfil semântico
  -> registro idempotente
  -> transporte e reconciliação
```

O parser não interpreta DTD.
O perfil não inventa regra externa.
O registro não aceita o mesmo `MsgId` com outro conteúdo.
O transporte não repete resultado incerto.
A reconciliação encerra o que a rede deixou ambíguo.

## Componentes

- `xml_security.py` — limites e parser;
- `validator.py` — regras por mensagem;
- `canonical.py` — representação estável e digest;
- `registry.py` — idempotência e estados;
- `reconciliation.py` — vínculo entre instrução e status;
- `builders.py` — construção determinística de `pacs.008`.

## O que não está aqui

- rede financeira;
- certificado de produção;
- assinatura XML institucional;
- XSD oficial;
- transporte persistente;
- banco de dados;
- autorização regulatória.

A ausência está registrada porque esconder dependência externa é começar a auditoria com uma mentira.
