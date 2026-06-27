# Ata de revisão técnica

**Data:** 2026-06-26  
**Responsável declarado:** Don Paulo Ricardo  
**Revisor independente:** pendente

## Decisões

1. não apresentar perfil sem XSD oficial como conformidade externa;
2. manter validação semântica local executável;
3. bloquear DTD, entidade externa e mensagens acima dos limites;
4. tratar `MsgId` como chave idempotente vinculada ao digest;
5. impedir reenvio em estado `UNKNOWN`;
6. exigir reconciliação antes de concluir resultado ambíguo;
7. manter assinatura e aprovação externas como pendências bloqueantes.

## Pendências

- seleção dos artefatos XSD aplicáveis;
- validação jurídica do direito de distribuição;
- homologação com infraestrutura externa;
- revisão independente;
- assinatura criptográfica real.
