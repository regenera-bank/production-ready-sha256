# Regenera — ISO 20022

**Documento:** ISO20022-BASELINE-001  
**Responsável declarado:** Don Paulo Ricardo  
**Estado:** pronto para revisão independente; ativação externa bloqueada

Mensagem financeira não é XML bonito.
É instrução que atravessa sistemas, certificados, filas e reconciliação.
Quando o significado fica ambíguo, o dinheiro não pode seguir no escuro.

Este pacote entrega uma base executável para quatro perfis:

- `pacs.008.001.08` — transferência de crédito entre instituições;
- `pacs.002.001.10` — status de pagamento;
- `camt.053.001.08` — extrato;
- `camt.054.001.08` — notificação de débito e crédito.

A validação local cobre estrutura, namespace, identificadores, valores, moeda,
regras de negócio, idempotência, estado `UNKNOWN`, reconciliação e segurança do parser.

## Limite que não será escondido

Os XSDs oficiais não estavam no pacote recebido.
Eles não foram inventados, reconstruídos ou apresentados como oficiais.
A homologação externa continua bloqueada até que os artefatos normativos corretos
sejam incorporados, versionados, verificados e aprovados pelo responsável competente.

## Execução

```sh
make all
```

O comando executa validação,  testes, varredura de segurança, build e verificação
da release. Não instala dependência. Não acessa rede. Não altera arquivo de origem.

## Fronteiras

- `src/regenera_iso20022/` — implementação ativa;
- `profiles/` — perfis internos e bloqueios externos;
- `tests/` — prova comportamental;
- `docs/` — decisões, políticas e operação;
- `governance/` — controles, owners, aprovação e procedência;
- `evidence/` — resultado gerado pelos gates;
- `build/release/` — pacote interno reproduzível.

Assinatura não se simula.
A aprovação criptográfica permanece pendente até existir chave real e revisão independente.
