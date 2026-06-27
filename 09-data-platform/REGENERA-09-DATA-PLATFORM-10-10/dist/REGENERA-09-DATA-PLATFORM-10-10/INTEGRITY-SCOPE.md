# Escopo de integridade

Os checksums internos cobrem todos os arquivos da release interna, exceto o próprio arquivo de checksums.

O hash externo do ZIP cobre:

- payload;
- políticas;
- código;
- testes;
- evidências;
- release interna reconstruída.

Não existe checksum autorreferente.
A prova nasce depois do artefato que pretende provar.
