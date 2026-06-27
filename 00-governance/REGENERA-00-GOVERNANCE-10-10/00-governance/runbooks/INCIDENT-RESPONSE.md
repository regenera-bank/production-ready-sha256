# Runbook — resposta a incidente

**Documento:** RUN-INC-001  
**Estado:** controlled  
**Autor responsável:** Don Paulo Ricardo  
**Owner operacional:** continuity-management  
**Vigência:** 2026-06-26  
**Próxima revisão:** 2026-12-23  
**Ciclo máximo:** 180 dias


## Severidade

| Nível | Critério | Ack | Comunicação executiva |
|---|---|---:|---:|
| SEV1 | efeito financeiro, exposição relevante, indisponibilidade crítica ou integridade incerta | 5 min | 15 min |
| SEV2 | degradação relevante com contenção disponível | 15 min | 30 min |
| SEV3 | impacto limitado sem risco sistêmico | 4 h | sob demanda |

## Autoridade

Incident Commander coordena. Domain Lead contém. Security Lead preserva evidência. Business Owner aceita retorno. Uma pessoa não acumula contenção e aceite final em SEV1.

## Declaração

Declare quando houver efeito financeiro, integridade incerta, dado exposto, controle crítico ineficaz ou indisponibilidade acima do limite.

## Procedimento

1. abrir registro e fixar horário T0;
2. nomear papéis e substitutos;
3. congelar mudanças não essenciais;
4. preservar logs, hashes e estado;
5. conter sem destruir prova;
6. identificar clientes, transações e dados afetados;
7. reconciliar efeito financeiro;
8. executar correção controlada;
9. validar observabilidade e backlog;
10. obter aceite de negócio e segurança;
11. comunicar encerramento;
12. abrir ações corretivas com owner e prazo.

## Critério de encerramento

Causa contida, integridade conhecida, reconciliação sem quebra, exposição delimitada, monitoramento estável e evidência preservada.

## Abort gate

Se o estado financeiro permanecer desconhecido, o incidente não encerra. Operação afetada permanece bloqueada.

## Evidência

Timeline, participantes, comandos, hashes, decisões, consultas, reconciliação, comunicação e aceite.
