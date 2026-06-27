# Runbook — Comprometimento de certificado ou credencial

**Documento:** INT-RUN-003  
**Severidade:** SEV1  
**Owner:** Security Engineering

## Declaração

Qualquer suspeita de chave privada exposta, certificado clonado, token privilegiado vazado ou uso fora do padrão.

## Contenção

1. revogar a credencial;
2. bloquear a rota ou fingerprint;
3. preservar logs de uso;
4. emitir material novo por canal independente;
5. notificar fornecedor e áreas obrigatórias;
6. revisar operações assinadas no período.

## Retorno

A nova credencial entra apenas após validação de fingerprint, teste mTLS e atualização de inventário. O material anterior permanece revogado.

## Evidências

Registro de revogação, emissão, aprovação, teste, janela de exposição e operações revisadas.
