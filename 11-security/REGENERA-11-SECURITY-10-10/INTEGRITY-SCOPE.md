# Escopo de integridade

`release/PAYLOAD-CHECKSUMS.sha256` cobre todos os arquivos de payload, testes e evidências geradas antes do build. Os arquivos do próprio diretório `release/` ficam fora da lista para evitar autorreferência.

O arquivo `.sha256` externo cobre o ZIP completo, incluindo payload e evidência. A assinatura `.asc` deve ser criada fora do ZIP com a chave institucional real.
