# Runbook — recuperação de desastre

**Documento:** RUN-DR-001  
**Estado:** controlled  
**Autor responsável:** Don Paulo Ricardo  
**Owner operacional:** continuity-management  
**Vigência:** 2026-06-26  
**Próxima revisão:** 2026-12-23  
**Ciclo máximo:** 180 dias


## Objetivos

- RTO contratado: 60 minutos;
- RPO contratado: 5 minutos;
- quebra financeira tolerada: 0;
- duplicidade financeira tolerada: 0.

## Papéis

Recovery Lead executa. Security Lead valida acesso e chaves. Data Lead valida integridade. Business Acceptance confirma retorno. Incident Commander decide avanço ou aborto.

## Pré-condições

Inventário vigente, backup íntegro, credenciais de emergência testadas, ordem de recuperação aprovada e canal de comunicação disponível.

## Sequência

1. declarar cenário e registrar T0;
2. bloquear escrita no ambiente comprometido;
3. selecionar ponto de recuperação;
4. verificar hash e cadeia do backup;
5. restaurar identidade, dados, ledger, mensageria e integrações nessa ordem;
6. validar constraints e contagens;
7. reconciliar saldos, eventos e mensagens;
8. medir RTO e RPO;
9. executar smoke test sem efeito financeiro real;
10. obter aceite segregado;
11. reabrir tráfego progressivamente;
12. manter observação reforçada.

## Abort gate

Pára se hash divergir, ledger não fechar, evento faltar, chave não for recuperável ou RPO exceder o limite sem aceite formal.

## Exercício

Trimestral para restauração. Semestral para perda de região. Resultado registra tempos observados, divergências, mensagens reprocessadas, duplicidades e achados.
