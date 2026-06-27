# Fraude material

**Documento:** RUN-RISK-002  
**Severidade:** SEV-1  
**RTO de contenção:** 15 minutos  
**Owner:** Fraud Risk

## Declaração

perda ativa, takeover ou duplicidade

## Papéis

- incidente: coordena e registra;
- owner: decide contenção;
- executor: aplica ação autorizada;
- auditor: preserva evidência;
- substituto: função formalmente designada.

## Procedimento

1. conter transação;
2. revogar sessão quando aplicável;
3. preservar sinais;
4. abrir caso;
5. reconciliar efeito financeiro;
6. decidir compensação.

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
