# Aplicação do pacote

1. Extraia o ZIP em diretório vazio.
2. Execute `make all` com Python 3.11 ou superior.
3. Confira `evidence/test/TEST-RESULTS.json` e `evidence/security/SECURITY-REPORT.json`.
4. Confira `release/PAYLOAD-CHECKSUMS.sha256` com `make verify-release`.
5. Substitua bloqueios externos somente por evidência real, identificada e assinada.
6. Assine o ZIP e o arquivo `.sha256` com a chave privada institucional.

Este pacote não contém credenciais, certificados privados, chaves privadas, resultados de pentest ou aprovações simuladas.
