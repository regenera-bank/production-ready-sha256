# Runbook — mudança incompatível

**Documento:** RB-CONTRACT-001  
**Severidade:** SEV-1 quando afeta operação financeira; SEV-2 nos demais casos

## Declaração

Declarar incidente quando consumidor rejeitar contrato publicado, evento deixar de ser desserializado ou resposta financeira mudar sem versão principal.

## Primeiros 15 minutos

1. congelar novas publicações;
2. identificar versão e hash distribuídos;
3. listar produtores e consumidores afetados;
4. restaurar a última versão assinada;
5. preservar logs, artefatos e diff;
6. abrir reconciliação quando houver efeito financeiro.

## Avançar

Avança somente quando:

- versão anterior foi restaurada;
- consumidor crítico voltou a processar;
- nenhuma duplicidade financeira foi criada;
- backlog de mensagens está sob controle.

## Encerrar

Encerrar após reconciliação, causa raiz, teste regressivo e aprovação do owner do domínio.

Rollback não apaga a versão quebrada.
Ela fica como evidência.
