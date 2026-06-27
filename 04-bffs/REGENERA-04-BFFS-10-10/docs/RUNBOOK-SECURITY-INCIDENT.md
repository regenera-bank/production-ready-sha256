# Runbook — incidente de segurança no BFF

**Severidade:** SEV-1 quando houver credencial, sessão ou dado financeiro exposto  
**Reconhecimento:** 5 minutos  
**Contenção inicial:** 15 minutos

1. Preserve correlation ids, hashes, logs e versão da release.
2. Revogue segredo, certificado ou sessão afetada.
3. Bloqueie a rota ou cliente sem apagar evidência.
4. Verifique replay, idempotência e efeitos financeiros associados.
5. Acione segurança, operação, jurídico e privacidade conforme o dado envolvido.
6. Reconcilie operações ambíguas.
7. Reabra tráfego somente com causa contida e gate aprovado.

O incidente não encerra quando o endpoint volta. Encerra quando o efeito, o alcance e a evidência estão fechados.
