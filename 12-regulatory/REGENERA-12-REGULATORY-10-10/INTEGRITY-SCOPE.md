# Escopo de integridade

`release/PAYLOAD-CHECKSUMS.sha256` cobre todos os arquivos de payload e evidência fora de `release/`.

A pasta `release/` é excluída para impedir autorreferência. O SHA-256 externo do ZIP cobre payload, evidência e metadados de release juntos.
