"""Núcleo verificável da plataforma de dados."""

from .money import Money
from .contracts import DataContract, DataField, ContractRegistry
from .ingestion import IngestionRegistry, IngestionStatus
from .quality import DataQualityGate, QualityRule
from .lineage import LineageChain
from .privacy import DataClass, PrivacyPolicy
from .retention import RetentionPolicy, RetentionRecord
from .access import AccessGrant, AccessPolicy
from .streaming import StreamProcessor
from .warehouse import SCD2Table
from .finance import reconcile_financial_rows
from .models import ModelRegistry

__all__ = [
    "Money", "DataContract", "DataField", "ContractRegistry",
    "IngestionRegistry", "IngestionStatus", "DataQualityGate", "QualityRule",
    "LineageChain", "DataClass", "PrivacyPolicy", "RetentionPolicy",
    "RetentionRecord", "AccessGrant", "AccessPolicy", "StreamProcessor",
    "SCD2Table", "reconcile_financial_rows", "ModelRegistry",
]
