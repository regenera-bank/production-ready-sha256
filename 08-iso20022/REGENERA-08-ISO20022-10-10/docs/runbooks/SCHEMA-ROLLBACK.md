# Rollback de schema

## Severidade
SEV1 quando houver risco financeiro, certificado comprometido ou reenvio possível.
SEV2 quando a falha estiver contida sem efeito financeiro.

## Declaração
O primeiro operador que comprovar o critério abre o incidente e registra correlação, horário e hash.

## Procedimento
1. interromper publicação da versão nova;
2. manter leitura da versão anterior;
3. bloquear mensagem incompatível;
4. restaurar artefatos pelo hash aprovado;
5. executar regressão completa;
6. registrar mensagens afetadas;
7. reativar somente após aprovação independente;

## Critério de avanço
Cada etapa exige evidência anexada. Falta de evidência mantém o bloqueio.

## Critério de encerramento
Causa identificada, impacto medido, reconciliação concluída, controle restaurado e revisão independente registrada.

## Evidência mínima
mensagem ou digest, código de erro, linha do tempo, decisões, aprovações e resultado dos testes.
