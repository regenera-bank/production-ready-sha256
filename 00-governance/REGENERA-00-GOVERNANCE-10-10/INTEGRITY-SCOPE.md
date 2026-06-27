# Escopo de integridade

- `00-governance/evidence/release/PAYLOAD-CHECKSUMS.sha256` cobre o payload controlado e exclui a própria evidência de release.
- o SHA-256 do ZIP completo é entregue fora do ZIP;
- nenhum checksum referencia arquivo ausente;
- a verificação do payload foi repetida após extração limpa;
- assinatura criptográfica depende da chave real de Don Paulo Ricardo e não é simulada.
