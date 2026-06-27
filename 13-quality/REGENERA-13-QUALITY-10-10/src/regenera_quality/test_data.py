from dataclasses import dataclass
from hashlib import sha256

@dataclass(frozen=True, slots=True)
class SyntheticCustomer:
    customer_id: str
    document_token: str
    email: str


def synthetic_customer(seed: str) -> SyntheticCustomer:
    if not seed or len(seed) < 8:
        raise ValueError("seed_too_short")
    digest = sha256(seed.encode()).hexdigest()
    return SyntheticCustomer(
        customer_id=f"syn-{digest[:16]}",
        document_token=f"tok-{digest[16:32]}",
        email=f"syn-{digest[32:44]}@example.invalid",
    )


def contains_real_contact(value: str) -> bool:
    lowered = value.lower()
    return any(domain in lowered for domain in ("@gmail.com", "@outlook.com", "@yahoo.com", "@hotmail.com"))
