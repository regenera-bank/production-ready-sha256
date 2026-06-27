# Política de exceções e risco aceito

**Documento:** POL-EXC-001  
**Estado:** controlled  
**Autor responsável:** Don Paulo Ricardo  
**Owner operacional:** governance-corporate  
**Vigência:** 2026-06-26  
**Próxima revisão:** 2026-12-23  
**Ciclo máximo:** 180 dias


## Escopo

Controles técnicos, operacionais, regulatórios e de segurança.

## Responsabilidades

O requester descreve o desvio. O owner propõe compensação. A autoridade de risco aceita. Auditoria acompanha vencimento.

## Evidências

Registro da exceção, análise de risco, compensação, aprovação, prazo, revisão e encerramento.

## Objetivo

Dar prazo, dono e consequência ao desvio. Exceção sem vencimento vira arquitetura paralela.

## Requisitos

Toda exceção registra:

- controle afetado;
- solicitante;
- owner;
- impacto;
- risco residual;
- compensação;
- autoridade de aceite;
- início e expiração;
- critério de encerramento;
- evidência de revisão.

## Limites

Exceção crítica tem validade máxima de 30 dias. Renovação exige nova análise. O solicitante não aprova a própria exceção.

## Expiração

Ao vencer, o controle retorna a `blocked`. Operação dependente da exceção para até correção ou novo aceite formal.

## Métricas

- exceções vencidas abertas: 0;
- exceções críticas acima de 30 dias: 0;
- exceções sem compensação: 0.
