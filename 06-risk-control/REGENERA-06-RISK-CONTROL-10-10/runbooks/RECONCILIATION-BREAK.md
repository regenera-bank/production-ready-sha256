# Quebra de reconciliação

**Documento:** RUN-CTRL-001  
**Severidade:** SEV-1  
**RTO de contenção:** 30 minutos  
**Owner:** Financial Control

## Declaração

diferença de valor, moeda ou ausência

## Papéis

- incidente: coordena e registra;
- owner: decide contenção;
- executor: aplica ação autorizada;
- auditor: preserva evidência;
- substituto: função formalmente designada.

## Procedimento

1. suspender reprocessamento cego;
2. identificar lado ausente;
3. conferir razão e provedor;
4. abrir caso;
5. compensar por lançamento;
6. fechar somente com saldo zero.

## Evidência mínima

- horário de declaração e encerramento;
- atores e decisões;
- hashes de entrada e saída;
- impacto financeiro e clientes afetados;
- ações de contenção e recuperação;
- aprovação de encerramento.

## Gates

Avança quando o fato está contido e a evidência fecha.
Aborta recuperação quando cria risco maior ou quebra financeira.

## Encerramento

Encerramento exige owner independente do executor e plano para cada achado.
Teste do runbook: semestral e após mudança material.
