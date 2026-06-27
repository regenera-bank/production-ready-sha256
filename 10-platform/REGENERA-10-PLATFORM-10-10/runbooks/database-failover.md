# Failover de banco

**Documento:** PLAT-RUN-DB-001  
**Severidade:** SEV-1 quando há efeito financeiro, perda de integridade ou indisponibilidade ampla  
**RTO:** 30 minutos  
**RPO:** 5 minutos

## Declaração

O incidente é declarado quando o indicador objetivo ultrapassa o limite ou quando o estado não pode ser confirmado.
Estado desconhecido não autoriza tentativa cega.

## Responsáveis

- Incident Commander: Operations accountable;
- executor: Platform Engineering;
- segurança: Security Operations;
- negócio: responsável pelo domínio afetado;
- comunicação executiva: autoridade registrada.

## Procedimento

1. congelar mudanças e registrar correlation ID;
2. capturar estado, métricas, logs e hashes;
3. confirmar escopo e integridade financeira;
4. escolher contenção com gate explícito;
5. executar somente ação aprovada;
6. reconciliar dados e efeitos financeiros;
7. medir RTO e RPO observados;
8. encerrar apenas com evidência e aceite independente.

## Abort gates

- hash divergente;
- reconciliação incompleta;
- replica lag acima do limite;
- identidade ou autorização não confirmada;
- risco de duplicação financeira;
- ausência de rollback comprovado.

## Evidência

Linha do tempo, comandos, responsáveis, hashes, métricas, divergências, decisão e aprovação de encerramento.
