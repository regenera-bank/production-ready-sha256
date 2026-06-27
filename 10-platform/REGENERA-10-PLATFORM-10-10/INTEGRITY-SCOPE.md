# Escopo de integridade

A integridade interna cobre todo arquivo de payload listado em `release/PAYLOAD-CHECKSUMS.sha256`.

A evidência gerada não entra no próprio checksum.
Hash que tenta provar a si mesmo cria ciclo. Ciclo não é cadeia de custódia.

O SHA-256 externo do ZIP cobre payload e evidência juntos.
A assinatura `.asc` deve ser criada com chave real e mantida fora do ZIP.
