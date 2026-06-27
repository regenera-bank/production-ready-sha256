# Arquitetura de risco e controle

## Fronteiras

```text
canais e core
    ↓
fraude | AML | KYC | sanções | crédito
    ↓
casos | auditoria | reconciliação | contabilidade | reporte
```

Decisão não edita fato.
Registra motivo.
Abre caso quando precisa.
Deixa prova quando fecha.

## Regras

- dinheiro usa centavos inteiros;
- provedor indisponível produz `UNKNOWN`;
- `UNKNOWN` não vira aprovação;
- lista de sanções não é aproximada por conveniência;
- crédito não recebe override silencioso;
- reconciliação tolera zero quebra financeira;
- contabilidade corrige por lançamento compensatório;
- caso crítico exige maker-checker;
- auditoria usa cadeia SHA-256;
- reporte não sai sem aprovação e payload íntegro.

## Dependências externas

Lista oficial, bureau, HSM, IAM, SIEM, fila e regulador ficam fora desta
biblioteca. Integração sem evidência permanece bloqueada.
