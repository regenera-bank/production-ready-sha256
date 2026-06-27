# Runbook de rollback de tokens

**Documento:** DS-RUN-TOK-001

## Quando usar

- contraste quebrado;
- token ausente;
- paridade divergente;
- layout crítico ilegível;
- consumer incompatível.

## Procedimento

1. registrar release afetada;
2. bloquear novos consumidores;
3. selecionar o hash anterior aprovado;
4. restaurar `tokens/` e saídas correspondentes;
5. reconstruir em diretório limpo;
6. comparar manifesto;
7. publicar o pacote inteiro;
8. validar consumidores prioritários.

Não edite arquivo gerado durante incidente.
Isso resolve a tela e destrói a origem.

## Critério de encerramento

- hashes iguais ao pacote aprovado;
- quatro saídas presentes;
- testes aprovados;
- consumidores críticos verificados;
- causa e ação preventiva registradas.
