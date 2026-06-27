# Runbook — restauração de dataset

**RTO alvo:** 60 minutos  
**RPO alvo:** 5 minutos  
**Owner:** data-platform

## Procedimento

1. declarar incidente e registrar tempo inicial;
2. selecionar backup pelo manifesto e hash;
3. restaurar em ambiente isolado;
4. validar checksums, contagem, contrato e qualidade;
5. reconciliar dados financeiros;
6. medir RTO e RPO observados;
7. promover somente com aceite independente.

Backup que nunca foi restaurado é esperança.
Não é controle.
