# Padrão de integridade de release

**Documento:** STD-REL-001  
**Estado:** controlled  
**Autor responsável:** Don Paulo Ricardo  
**Owner operacional:** engineering-governance  
**Vigência:** 2026-06-26  
**Próxima revisão:** 2026-12-23  
**Ciclo máximo:** 180 dias


## Conteúdo mínimo

- versão;
- payload manifest;
- checksums;
- SBOM;
- resultados de validação, teste e segurança;
- proveniência de build;
- aprovação;
- rollback;
- hash externo do ZIP.

## Reprodutibilidade

Arquivos recebem timestamp fixo no ZIP. Ordem é lexicográfica. Cache, metadata de sistema e evidência antiga são excluídos.

## Verificação

O verificador extrai em diretório limpo, confere paths, hashes e executa os controles offline.
