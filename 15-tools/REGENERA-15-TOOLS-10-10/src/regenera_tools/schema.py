from __future__ import annotations
import json,re
from typing import Any
from .errors import ValidationError

def parse_json_strict(text: str) -> Any:
    def pairs(values):
        out={}
        for key,value in values:
            if key in out: raise ValidationError(f"chave duplicada:{key}")
            out[key]=value
        return out
    try: return json.loads(text,object_pairs_hook=pairs)
    except json.JSONDecodeError as exc: raise ValidationError(f"json inválido:{exc.msg}") from exc

def _type_ok(value: Any, expected: str) -> bool:
    return {"object":isinstance(value,dict),"array":isinstance(value,list),"string":isinstance(value,str),"integer":isinstance(value,int) and not isinstance(value,bool),"number":isinstance(value,(int,float)) and not isinstance(value,bool),"boolean":isinstance(value,bool),"null":value is None}.get(expected,False)

def validate(instance: Any, schema: dict[str,Any], path: str="$", errors: list[str]|None=None) -> list[str]:
    errors=[] if errors is None else errors
    expected=schema.get("type")
    if expected and not _type_ok(instance,expected): errors.append(f"{path}:tipo esperado {expected}"); return errors
    if "enum" in schema and instance not in schema["enum"]: errors.append(f"{path}:valor fora do enum")
    if isinstance(instance,str):
        if len(instance)<schema.get("minLength",0): errors.append(f"{path}:texto curto")
        if "maxLength" in schema and len(instance)>schema["maxLength"]: errors.append(f"{path}:texto longo")
        if "pattern" in schema and re.fullmatch(schema["pattern"],instance) is None: errors.append(f"{path}:formato inválido")
    if isinstance(instance,(int,float)) and not isinstance(instance,bool):
        if "minimum" in schema and instance<schema["minimum"]: errors.append(f"{path}:abaixo do mínimo")
        if "maximum" in schema and instance>schema["maximum"]: errors.append(f"{path}:acima do máximo")
    if isinstance(instance,dict):
        for key in schema.get("required",[]):
            if key not in instance: errors.append(f"{path}.{key}:obrigatório")
        props=schema.get("properties",{})
        if schema.get("additionalProperties") is False:
            for key in instance:
                if key not in props: errors.append(f"{path}.{key}:campo não permitido")
        for key,sub in props.items():
            if key in instance: validate(instance[key],sub,f"{path}.{key}",errors)
    if isinstance(instance,list) and "items" in schema:
        for i,item in enumerate(instance): validate(item,schema["items"],f"{path}[{i}]",errors)
    return errors
