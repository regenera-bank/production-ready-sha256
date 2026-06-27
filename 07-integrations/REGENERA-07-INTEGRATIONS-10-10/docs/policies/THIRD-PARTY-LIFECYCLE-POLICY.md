# Política de Ciclo de Vida de Terceiros

**Documento:** INT-POL-003  
**Vigência técnica:** 26 de junho de 2026  
**Revisão:** anual

## Objetivo

Controlar entrada, mudança, operação e desligamento de provedores externos.

## Escopo

Aplica-se aos quatorze adaptadores registrados e a qualquer novo terceiro com acesso a dados, pagamentos, liquidação, custódia ou reporte.

## Responsabilidades

- Vendor Management mantém contrato e criticidade.
- Jurídico valida obrigações, tratamento de dados e saída.
- Security Engineering avalia controles e incidentes.
- Owner do domínio aceita o risco residual.
- Release Engineering bloqueia ativação sem evidência.

## Controles obrigatórios

1. Due diligence antes da homologação.
2. Classificação de criticidade e dados tratados.
3. SLA, RTO, RPO e janela de suporte definidos.
4. Direito de auditoria e notificação de incidente previsto.
5. Plano de saída e portabilidade testável.
6. Subprocessadores declarados.
7. Mudança contratual dispara revisão técnica.
8. Evidência externa possui validade e owner.
9. Provedor suspenso não pode receber tráfego novo.
10. Desligamento revoga credencial, certificado e rota.

## Evidências

- contrato e aditivos;
- relatório de due diligence;
- homologação;
- inventário de dados;
- teste de contingência;
- registro de subprocessadores;
- evidência de revogação no desligamento.

## Exceções

Exceção de terceiro crítico exige aprovação executiva, prazo curto, controle compensatório e plano de substituição.

## Revisão

Revisão anual, na renovação contratual, após incidente ou mudança material do serviço.
