# Mensagem duplicada

## Severidade
SEV1 quando houver risco financeiro, certificado comprometido ou reenvio possível.
SEV2 quando a falha estiver contida sem efeito financeiro.

## Declaração
O primeiro operador que comprovar o critério abre o incidente e registra correlação, horário e hash.

## Procedimento
1. comparar MsgId e digest;
2. mesmo digest retorna resultado original;
3. digest diferente bloqueia como conflito;
4. não criar segunda instrução;
5. preservar evidência e correlação;
6. investigar origem da duplicidade;

## Critério de avanço
Cada etapa exige evidência anexada. Falta de evidência mantém o bloqueio.

## Critério de encerramento
Causa identificada, impacto medido, reconciliação concluída, controle restaurado e revisão independente registrada.

## Evidência mínima
mensagem ou digest, código de erro, linha do tempo, decisões, aprovações e resultado dos testes.
