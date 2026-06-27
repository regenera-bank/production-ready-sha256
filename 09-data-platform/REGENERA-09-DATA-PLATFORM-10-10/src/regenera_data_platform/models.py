from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone


class ModelGovernanceError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class ModelVersion:
    model_id: str
    version: str
    artifact_hash: str
    dataset_fingerprint: str
    owner_group: str
    metric_name: str
    metric_value: float
    minimum_metric: float
    approved_by: str | None = None
    approved_at: datetime | None = None


class ModelRegistry:
    def __init__(self) -> None:
        self._versions: dict[tuple[str, str], ModelVersion] = {}

    def register(self, version: ModelVersion) -> None:
        if len(version.artifact_hash) != 64 or len(version.dataset_fingerprint) != 64:
            raise ModelGovernanceError("hash de artefato ou dataset inválido")
        if not version.owner_group:
            raise ModelGovernanceError("owner obrigatório")
        self._versions[(version.model_id, version.version)] = version

    def activate(self, model_id: str, version: str, actor: str) -> ModelVersion:
        try:
            item = self._versions[(model_id, version)]
        except KeyError as exc:
            raise ModelGovernanceError("modelo não registrado") from exc
        if item.metric_value < item.minimum_metric:
            raise ModelGovernanceError("métrica abaixo do limite")
        if not item.approved_by or item.approved_by == actor:
            raise ModelGovernanceError("aprovação independente obrigatória")
        if not item.approved_at or item.approved_at.astimezone(timezone.utc) > datetime.now(timezone.utc):
            raise ModelGovernanceError("aprovação inválida")
        return item
