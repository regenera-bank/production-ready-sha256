# Ata de revisão técnica

**Escopo:** controles de segurança do Regenera Bank.  
**Responsável técnico declarado:** Don Paulo Ricardo.  
**Decisão:** aprovar a verificação técnica local e manter ativação externa bloqueada.

## Critérios aplicados

- nenhum controle é considerado ativo sem owner, evidência e prazo de revisão;
- acesso privilegiado exige identidade forte, MFA, prazo e aprovação independente;
- segredo estático, chave privada em repositório e artefato sem hash são bloqueados;
- vulnerabilidade crítica vencida impede release;
- exceção autoaprovada ou vencida é inválida;
- incidente não encerra sem evidência, causa, contenção e aprovação independente;
- resultados externos não são simulados.
