# Regenera Bank — Regulatory Control Plane

Pacote consolidado de controles regulatórios. A finalidade é manter obrigação, prazo, evidência, aprovação, submissão e reconciliação sob estados explícitos e auditáveis.

## O que este pacote comprova

- catálogo de 14 domínios regulatórios;
- calendário sem datas legais inventadas;
- evidência imutável depois da aprovação;
- maker-checker e aprovação vinculada ao digest;
- relatório determinístico;
- submissão idempotente;
- estado `UNKNOWN` para resultado externo ambíguo;
- reconciliação de protocolo e conteúdo;
- privacidade, retenção e legal hold;
- trilha encadeada por SHA-256;
- controles, exceções, políticas e runbooks;
- build reproduzível sem rede e sem dependências de terceiros.

## O que este pacote não afirma

Não existe neste artefato protocolo oficial, aceite de regulador, parecer jurídico, homologação, certificado institucional ou assinatura criptográfica. Datas, leiautes e canais oficiais permanecem bloqueados até configuração e evidência externa aprovadas.

## Execução

```bash
make all
```

A saída precisa encerrar com validação, testes, security scan, build e verificação de checksums aprovados.
