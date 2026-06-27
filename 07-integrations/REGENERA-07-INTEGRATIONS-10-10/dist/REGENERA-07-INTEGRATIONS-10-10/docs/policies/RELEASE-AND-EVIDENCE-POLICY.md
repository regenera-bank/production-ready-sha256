# Política de Release e Evidência das Integrações

**Documento:** INT-POL-004  
**Vigência técnica:** 26 de junho de 2026  
**Revisão:** anual

## Objetivo

Garantir que cada release seja reproduzível, íntegra e ligada à aprovação que a autorizou.

## Escopo

Aplica-se ao kernel, adaptadores, schemas, configurações e documentação operacional.

## Responsabilidades

- autor prepara a mudança;
- revisor independente valida risco e evidência;
- Release Engineering produz manifesto, SBOM e checksum;
- aprovador autorizado assina o artefato;
- Operations promove entre ambientes.

## Controles obrigatórios

1. autor não aprova a própria release;
2. testes, validação e security scan precisam passar;
3. manifesto cobre a árvore distribuída;
4. checksum interno não se autorreferencia;
5. hash externo cobre o ZIP final;
6. assinatura usa chave real fora do pacote;
7. artefato não contém segredo, cache ou arquivo de sistema;
8. rollback e compatibilidade são conhecidos antes da promoção;
9. evidência corresponde ao artefato entregue;
10. ativação externa exige homologação vigente.

## Evidências

- pull request e revisão;
- resultados de testes;
- manifesto;
- SBOM;
- proveniência;
- checksum;
- assinatura `.asc`;
- ticket de mudança;
- validação pós-deploy.

## Exceções

Release emergencial exige dupla aprovação, prazo de regularização e retrospectiva. Ausência de assinatura não é exceção aceitável para produção.

## Revisão

Revisão anual e após qualquer divergência entre evidência e pacote distribuído.
