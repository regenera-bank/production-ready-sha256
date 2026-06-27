# Ata de revisão técnica

**Data:** 2026-06-26  
**Responsável pela reconstrução:** Don Paulo Ricardo  
**Escopo:** operações bancárias  

## Decisões

- consolidar controles compartilhados em um pacote único;
- usar unidade mínima inteira para valores monetários;
- tratar timeout financeiro como estado `UNKNOWN`;
- exigir segregação para aprovação, fechamento e exceção;
- impedir encerramento sem evidência vinculada;
- manter integrações externas como bloqueios formais.

## Estado

Verificação técnica local: concluída.  
Aprovação institucional: pendente.  
Assinatura criptográfica: pendente.  
Revisão independente externa: pendente.
