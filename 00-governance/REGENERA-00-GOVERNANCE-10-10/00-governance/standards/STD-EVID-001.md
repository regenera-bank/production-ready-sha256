# Padrão de evidência técnica

**Documento:** STD-EVID-001  
**Estado:** controlled  
**Autor responsável:** Don Paulo Ricardo  
**Owner operacional:** governance-corporate  
**Vigência:** 2026-06-26  
**Próxima revisão:** 2026-12-23  
**Ciclo máximo:** 180 dias


## Propriedades

Evidência válida possui origem, horário, executor, comando, exit code, hash e relação com o controle.

## Cadeia de custódia

1. coletar sem alterar a fonte;
2. calcular SHA-256;
3. registrar origem e destino;
4. limitar acesso;
5. preservar versão bruta;
6. produzir análise separada;
7. registrar qualquer transformação.

## Estados

- `raw`: saída original;
- `verified`: hash conferido;
- `reviewed`: revisão nominal concluída;
- `approved`: autoridade independente aceitou;
- `superseded`: preservada, mas substituída;
- `invalid`: não sustenta a afirmação.

## Regra

Relatório narrativo não substitui log bruto.
