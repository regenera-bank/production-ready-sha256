# Regenera Bank — Integrações Externas

**Documento:** INT-BASELINE-001  
**Estado:** pronto para validação técnica; ativação externa bloqueada  
**Responsável técnico declarado:** Don Paulo Ricardo

Integração não é chamada HTTP com nome bonito.
É uma fronteira onde o banco perde controle sobre tempo, estado e resposta.

Este pacote entrega o kernel comum, o registro dos adaptadores, os controles de segurança, a reconciliação e a prova local. Não declara conexão produtiva com SPI, DICT, Open Finance, Bacen, B3, SUSEP, SWIFT, bandeiras, processadores, custodiantes, bureaus ou provedores.

## Conteúdo

- kernel de idempotência, retry e circuit breaker;
- estado `UNKNOWN` para falha após envio;
- reconciliação por referência, valor e moeda;
- política de endpoint, mTLS e HMAC;
- registro dos 14 adaptadores;
- controles e bloqueios externos;
- testes comportamentais;
- build determinístico, manifesto, SBOM e checksums.

## Execução

```bash
make all
```

O comando limpa, valida, testa, executa o scan de segurança, monta a release e confere todos os hashes.

## Limite

Homologação não se inventa.
Certificado não se simula.
Canal externo só entra em produção quando a instituição do outro lado reconhece a conexão e a evidência está assinada.
