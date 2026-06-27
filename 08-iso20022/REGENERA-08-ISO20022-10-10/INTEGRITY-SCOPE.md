# Escopo de integridade

`PACKAGE-CHECKSUMS.sha256` cobre todos os arquivos da release interna, exceto ele próprio.
Autorreferência não prova nada; apenas cria ciclo.

O hash externo do ZIP cobre a distribuição inteira, incluindo manifesto, evidência e checksums.

A release falha quando:

- um arquivo coberto muda;
- um arquivo coberto desaparece;
- aparece arquivo inesperado;
- os resultados dos gates não estão aprovados;
- o pacote contém resíduo de sistema, ZIP aninhado, segredo ou chave privada.
