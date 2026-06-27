# Runbook — pagamento em estado UNKNOWN

**Severidade inicial:** SEV-2  
**Owner operacional:** Core Banking Operations  
**Escalonamento:** Payments, Ledger, Integrações e Segurança quando houver suspeita de fraude

## Declaração

Estado `UNKNOWN` significa que o resultado externo não está provado.
Não significa falha.
Não significa sucesso.

## Entrada

Abrir o runbook quando:

- houve timeout depois do envio;
- a conexão caiu sem resposta conclusiva;
- o provedor retornou referência inconsistente;
- a confirmação não chegou no SLA;
- ledger e provedor discordam.

## Procedimento

1. congelar retry automático da operação;
2. registrar payment_id, correlation_id, EndToEndId e horário;
3. validar o lançamento local e o hash da evidência;
4. consultar o provedor por identificador idempotente;
5. consultar mensageria e callback;
6. comparar valor, moeda, participante e estado;
7. anexar resposta externa ao caso;
8. resolver como `SETTLED` ou `REJECTED`;
9. se rejeitado, criar reversão compensatória;
10. validar saldo e reconciliação depois da decisão.

## Abort gates

Interromper e escalar para SEV-1 quando:

- existir mais de um efeito externo para a mesma chave;
- o ledger estiver desequilibrado;
- a referência externa pertencer a outro valor ou participante;
- houver indício de adulteração;
- não for possível provar qual sistema executou o efeito.

## Encerramento

O caso encerra somente com:

- evidência externa;
- decisão registrada;
- ledger validado;
- ausência de quebra;
- responsável nominal;
- hash dos documentos anexos.
