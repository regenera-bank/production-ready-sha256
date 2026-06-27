# Ata de revisão técnica

**Data:** 2026-06-26  
**Responsável declarado:** Don Paulo Ricardo

## Decisões

- separar controle verificável de infraestrutura externa;
- recusar credencial estática em workload;
- exigir artefato por digest e assinatura;
- exigir aprovação segregada;
- exigir restauração testada para considerar backup eficaz;
- tratar resultado de failover ambíguo como `UNKNOWN`;
- impedir que RTO ou RPO sejam declarados sem medição.

## Pendências bloqueantes

- contas cloud e landing zone;
- HSM/KMS e rotação real;
- clusters Kubernetes;
- bancos gerenciados;
- SIEM e observabilidade institucional;
- região de DR;
- revisão independente e assinatura.
