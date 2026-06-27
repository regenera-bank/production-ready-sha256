# Aplicação

1. Execute `make all` em ambiente limpo com Python 3.11 ou superior.
2. Revise `evidence/results/TEST-RESULTS.json`.
3. Revise `evidence/results/SECURITY-REPORT.json`.
4. Revise `evidence/results/RELEASE-GATE.json`.
5. Confirme `evidence/PAYLOAD-CHECKSUMS.sha256` com `python3 tools/verify_release.py`.
6. Assine o ZIP externamente com a chave institucional real.

A aprovação técnica local não substitui aceite institucional, homologação ou assinatura criptográfica.
