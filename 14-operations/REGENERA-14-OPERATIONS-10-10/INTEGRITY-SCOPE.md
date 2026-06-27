# Escopo de integridade

`PAYLOAD-MANIFEST.json` e `PAYLOAD-CHECKSUMS.sha256` cobrem todos os arquivos internos, exceto os dois próprios arquivos de integridade. Essa exclusão evita autorreferência impossível.

O hash SHA-256 externo do ZIP cobre payload, evidências e arquivos de integridade juntos.
