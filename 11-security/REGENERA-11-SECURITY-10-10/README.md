# Regenera Bank — Security Controls

**Documento:** SECURITY-BASELINE-001  
**Versão:** 10.10  
**Estado:** verificação técnica aprovada; assinatura e aprovação institucional pendentes.

Este pacote contém controles executáveis de segurança, políticas, runbooks, testes e evidências reproduzíveis. Ele não declara HSM, PKI, SIEM, pentest, red team, cloud ou homologação externa como ativos sem prova real.

## Fronteiras ativas

- identidade, acesso e privilégio temporário;
- segregação de funções e maker-checker;
- segredos, rotação e metadados de chaves;
- secure SDLC e gate de release;
- vulnerabilidades, SLA e exceções;
- proveniência e integridade de artefatos;
- detecção, alerta e cadeia de auditoria;
- resposta a incidentes e preservação de evidência;
- controles mobile, cloud e infraestrutura como políticas verificáveis;
- registro de riscos e bloqueios externos.

## Execução

```bash
make all
```

O comando limpa resíduos, valida a estrutura, executa os testes, procura segredos, gera evidências e verifica todos os hashes do payload.

## Estado externo

A release permanece `UNSIGNED_PENDING_EXTERNAL_APPROVAL`. A assinatura `.asc`, aprovação independente e evidências operacionais precisam ser produzidas por pessoas, chaves e ambientes reais.
