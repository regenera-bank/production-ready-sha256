# Quebra da cadeia de auditoria

**Documento:** RUN-CTRL-002  
**Severidade:** SEV-1  
**RTO de contenção:** 15 minutos  
**Owner:** Control Assurance

## Declaração

hash anterior ou hash do evento diverge

## Papéis

- incidente: coordena e registra;
- owner: decide contenção;
- executor: aplica ação autorizada;
- auditor: preserva evidência;
- substituto: função formalmente designada.

## Procedimento

1. congelar fonte;
2. coletar cópia somente leitura;
3. calcular hashes;
4. restringir acesso;
5. escalar segurança e jurídico;
6. restaurar apenas de fonte íntegra.

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
