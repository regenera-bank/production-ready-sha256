# Política de dados e segredos

**Documento:** POL-CORE-003  
**Owner declarado:** Don Paulo Ricardo  
**Revisão:** anual

## Regras

- segredo não entra em código, migration, log ou evidência;
- chave Pix não permanece em claro fora do fluxo estritamente necessário;
- token de sessão não é persistido em claro;
- identificador sensível usa máscara para suporte e hash/HMAC para busca;
- dado financeiro em telemetria precisa de allowlist;
- dump produtivo não entra em ambiente de desenvolvimento;
- evidência regulatória usa minimização e controle de acesso;
- rotação de chave precisa preservar capacidade de leitura quando aplicável;
- material criptográfico depende de secret manager ou HSM aprovado.

## Exceções

Não existe exceção para chave privada em repositório.
Achado confirmado exige contenção, rotação e análise de histórico.
