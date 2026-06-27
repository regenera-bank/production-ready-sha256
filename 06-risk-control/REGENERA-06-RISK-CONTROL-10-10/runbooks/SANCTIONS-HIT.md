# Hit de sanções

**Documento:** RUN-RISK-001  
**Severidade:** SEV-1  
**RTO de contenção:** 15 minutos  
**Owner:** Compliance Risk

## Declaração

hit confirmado ou lista inconsistente

## Papéis

- incidente: coordena e registra;
- owner: decide contenção;
- executor: aplica ação autorizada;
- auditor: preserva evidência;
- substituto: função formalmente designada.

## Procedimento

1. bloquear decisão;
2. preservar entrada e versão da lista;
3. abrir caso;
4. notificar owner;
5. validar falso positivo;
6. liberar ou manter bloqueio com aprovação.

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
