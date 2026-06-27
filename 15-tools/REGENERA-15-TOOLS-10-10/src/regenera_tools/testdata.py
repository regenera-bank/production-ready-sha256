from __future__ import annotations
import hashlib,hmac

class SyntheticData:
    def __init__(self, seed: str):
        if len(seed)<16: raise ValueError("seed precisa ter ao menos 16 caracteres")
        self.key=seed.encode()
    def _hex(self,label:str,index:int,length:int)->str:
        return hmac.new(self.key,f"{label}:{index}".encode(),hashlib.sha256).hexdigest()[:length]
    def customer(self,index:int)->dict[str,str]:
        if index<0: raise ValueError("índice inválido")
        token=self._hex("customer",index,16)
        return {"customer_id":f"SYN-{token}","name":f"Pessoa Sintética {index:04d}","email":f"synthetic-{token}@example.invalid"}
    def transaction(self,index:int)->dict[str,object]:
        token=self._hex("transaction",index,20)
        return {"transaction_id":f"SYN-TX-{token}","amount_minor":100+index,"currency":"BRL","synthetic":True}
