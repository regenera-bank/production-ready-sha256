# Aplicação controlada

1. valide o SHA-256 externo;
2. valide a assinatura `.asc`;
3. extraia em diretório novo;
4. execute `make all`;
5. revise `release/CONTROL-STATUS.json`;
6. bloqueie promoção se existir dependência externa sem evidência;
7. aplique por pull request assinado, com autor e aprovador diferentes.

Não copie por cima de ambiente ativo.
Plataforma muda primeiro em staging. Produção vem depois da prova.
