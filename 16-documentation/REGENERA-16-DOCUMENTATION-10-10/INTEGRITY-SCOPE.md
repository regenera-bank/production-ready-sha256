# Escopo de integridade

`evidence/PAYLOAD-CHECKSUMS.sha256` cobre todos os arquivos de payload, incluindo o site estático gerado e excluindo apenas a própria evidência para evitar autorreferência.

O hash externo do ZIP cobre:

- payload;
- evidências;
- manifestos;
- relatórios;
- logs.

A assinatura `.asc` é externa e não é simulada.
