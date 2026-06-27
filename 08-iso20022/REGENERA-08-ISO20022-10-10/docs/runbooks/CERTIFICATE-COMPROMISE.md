# Comprometimento de certificado

## Severidade
SEV1 quando houver risco financeiro, certificado comprometido ou reenvio possível.
SEV2 quando a falha estiver contida sem efeito financeiro.

## Declaração
O primeiro operador que comprovar o critério abre o incidente e registra correlação, horário e hash.

## Procedimento
1. declarar SEV1;
2. bloquear emissão;
3. revogar credencial comprometida;
4. rotacionar em cofre aprovado;
5. validar fingerprints e trust stores;
6. reprocessar somente mensagens não enviadas;
7. reconciliar janela de exposição;
8. obter aprovação de retorno;

## Critério de avanço
Cada etapa exige evidência anexada. Falta de evidência mantém o bloqueio.

## Critério de encerramento
Causa identificada, impacto medido, reconciliação concluída, controle restaurado e revisão independente registrada.

## Evidência mínima
mensagem ou digest, código de erro, linha do tempo, decisões, aprovações e resultado dos testes.
