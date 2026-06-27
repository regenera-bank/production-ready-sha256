from __future__ import annotations
from typing import Any

MUTATING={"post","put","patch","delete"}

def lint_openapi(doc: dict[str,Any]) -> list[str]:
    errors=[]
    if not str(doc.get("openapi","")).startswith("3.1."): errors.append("openapi precisa ser 3.1")
    if not isinstance(doc.get("info"),dict) or not doc["info"].get("title") or not doc["info"].get("version"): errors.append("info incompleto")
    paths=doc.get("paths")
    if not isinstance(paths,dict) or not paths: errors.append("paths ausente"); return errors
    ids=set()
    for route,item in paths.items():
        if not route.startswith("/"): errors.append(f"path inválido:{route}")
        if not isinstance(item,dict): continue
        for method,operation in item.items():
            if method.lower() not in {"get","post","put","patch","delete","options","head"} or not isinstance(operation,dict): continue
            opid=operation.get("operationId")
            if not opid: errors.append(f"operationId ausente:{method}:{route}")
            elif opid in ids: errors.append(f"operationId duplicado:{opid}")
            else: ids.add(opid)
            responses=operation.get("responses",{})
            if not responses: errors.append(f"responses ausente:{opid or route}")
            if method.lower() in MUTATING:
                params=operation.get("parameters",[])
                found=any(p.get("in")=="header" and p.get("name","").lower()=="idempotency-key" and p.get("required") is True for p in params if isinstance(p,dict))
                if not found: errors.append(f"idempotência ausente:{opid or route}")
                if "409" not in responses: errors.append(f"resposta 409 ausente:{opid or route}")
    return errors

def lint_asyncapi(doc: dict[str,Any]) -> list[str]:
    errors=[]
    if not str(doc.get("asyncapi","")).startswith("3.0."): errors.append("asyncapi precisa ser 3.0")
    channels=doc.get("channels")
    if not isinstance(channels,dict) or not channels: errors.append("channels ausente"); return errors
    addresses=set()
    for name,channel in channels.items():
        address=channel.get("address") if isinstance(channel,dict) else None
        if not address: errors.append(f"address ausente:{name}")
        elif address in addresses: errors.append(f"address duplicado:{address}")
        else: addresses.add(address)
        messages=channel.get("messages",{}) if isinstance(channel,dict) else {}
        if not messages: errors.append(f"messages ausente:{name}")
    return errors
