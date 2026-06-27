# Relatório de verificação da release

**Documento:** RELEASE-EVIDENCE-001  
**Estado:** verificado tecnicamente  
**Autor responsável:** Don Paulo Ricardo  
**Owner operacional:** Engenharia de Plataforma  
**Vigência:** 2026-06-26  
**Próxima revisão:** 2027-06-26  
**Data da execução:** 2026-06-26  

## Resultado

Todos os comandos definidos pela própria árvore concluíram com código de retorno zero nesta execução.

| Verificação | Resultado |
|---|---|
| limpeza | PASS |
| validação estrutural | PASS |
| testes comportamentais | PASS — 24 testes |
| varredura de segredo | PASS |
| exercício local de restauração | PASS |
| build determinístico | PASS |
| verificação após extração limpa | PASS |
| varredura de conteúdo proibido | PASS |

## Riscos exercitados

- lançamento desequilibrado é recusado;
- moedas distintas não fecham o mesmo lançamento;
- lançamento postado é imutável;
- estorno preserva o original e cria compensação;
- duplicidade devolve o resultado original;
- estado UNKNOWN bloqueia repetição cega;
- autoaprovação é recusada;
- aprovação sem assinatura é recusada;
- exceção vencida é recusada;
- owner ausente torna o controle ineficaz;
- evidência ausente torna o controle ineficaz;
- restauração confere o hash da origem e da cópia.

## Continuidade

O exercício foi executado sobre conjunto sintético local. Ele prova o mecanismo de backup, remoção, restauração e comparação de hash desta release. Não substitui exercício de região, fornecedor ou banco produtivo.

- hash de origem: `4940de393cf9c3fef45752b92dc9c05fc045d21710f01516ed0907fe4d3e2178`;
- hash restaurado: `4940de393cf9c3fef45752b92dc9c05fc045d21710f01516ed0907fe4d3e2178`;
- integridade: `true`;
- RTO observado no exercício local: `9.084 ms`;
- quebras financeiras: `0`;
- efeitos duplicados: `0`.

## Integridade

`PAYLOAD-CHECKSUMS.sha256` cobre o payload de `00-governance`, exceto `evidence/release`, porque a evidência nasce depois do payload validado.

O SHA-256 do ZIP final é entregue em arquivo externo. Isso evita autorreferência e prova exatamente o arquivo distribuído.

## Ativação institucional

A validação técnica está concluída. A ativação institucional continua condicionada a:

1. commit assinado por Don Paulo Ricardo no repositório fonte;
2. aprovação independente assinada;
3. assinatura destacada do ZIP com chave real;
4. registro da identidade da chave e do verificador.

Sem esses quatro itens, a release permanece bloqueada para promoção institucional.
