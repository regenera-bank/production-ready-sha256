# Entrega em estado UNKNOWN

## Severidade
SEV1 quando houver risco financeiro, certificado comprometido ou reenvio possível.
SEV2 quando a falha estiver contida sem efeito financeiro.

## Declaração
O primeiro operador que comprovar o critério abre o incidente e registra correlação, horário e hash.

## Procedimento
1. marcar mensagem como UNKNOWN;
2. bloquear reenvio automático;
3. consultar status pelo identificador original;
4. comparar pacs.002, camt e registro interno;
5. escalar após 15 minutos sem prova;
6. mover para reconciliação manual;
7. encerrar apenas com ACK ou rejeição comprovada;

## Critério de avanço
Cada etapa exige evidência anexada. Falta de evidência mantém o bloqueio.

## Critério de encerramento
Causa identificada, impacto medido, reconciliação concluída, controle restaurado e revisão independente registrada.

## Evidência mínima
mensagem ou digest, código de erro, linha do tempo, decisões, aprovações e resultado dos testes.
