# Quebra de reconciliação

## Severidade
SEV1 quando houver risco financeiro, certificado comprometido ou reenvio possível.
SEV2 quando a falha estiver contida sem efeito financeiro.

## Declaração
O primeiro operador que comprovar o critério abre o incidente e registra correlação, horário e hash.

## Procedimento
1. bloquear fechamento do lote;
2. separar ausência, duplicidade, valor, moeda e estado;
3. preservar mensagens e digests;
4. não ajustar saldo manualmente;
5. criar correção compensatória quando aplicável;
6. obter revisão de segunda pessoa;
7. encerrar com divergência zero ou risco aceito formalmente;

## Critério de avanço
Cada etapa exige evidência anexada. Falta de evidência mantém o bloqueio.

## Critério de encerramento
Causa identificada, impacto medido, reconciliação concluída, controle restaurado e revisão independente registrada.

## Evidência mínima
mensagem ou digest, código de erro, linha do tempo, decisões, aprovações e resultado dos testes.
