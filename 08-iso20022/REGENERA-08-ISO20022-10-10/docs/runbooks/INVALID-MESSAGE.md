# Mensagem inválida

## Severidade
SEV1 quando houver risco financeiro, certificado comprometido ou reenvio possível.
SEV2 quando a falha estiver contida sem efeito financeiro.

## Declaração
O primeiro operador que comprovar o critério abre o incidente e registra correlação, horário e hash.

## Procedimento
1. preservar hash e metadados sem expor dado sensível;
2. classificar erro de XML, namespace, schema ou regra;
3. bloquear encaminhamento;
4. notificar owner do perfil;
5. corrigir somente com nova versão e evidência;
6. encerrar depois de reproduzir e testar;

## Critério de avanço
Cada etapa exige evidência anexada. Falta de evidência mantém o bloqueio.

## Critério de encerramento
Causa identificada, impacto medido, reconciliação concluída, controle restaurado e revisão independente registrada.

## Evidência mínima
mensagem ou digest, código de erro, linha do tempo, decisões, aprovações e resultado dos testes.
