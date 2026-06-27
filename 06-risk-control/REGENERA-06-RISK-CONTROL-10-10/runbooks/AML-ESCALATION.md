# Escalonamento AML

**Documento:** RUN-RISK-003  
**Severidade:** SEV-2  
**RTO de contenção:** 4 horas  
**Owner:** Compliance Risk

## Declaração

score crítico, estruturação ou sanção

## Papéis

- incidente: coordena e registra;
- owner: decide contenção;
- executor: aplica ação autorizada;
- auditor: preserva evidência;
- substituto: função formalmente designada.

## Procedimento

1. congelar decisão;
2. reunir transações relacionadas;
3. registrar regra e score;
4. designar analista;
5. aprovar disposição;
6. preservar relatório.

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
