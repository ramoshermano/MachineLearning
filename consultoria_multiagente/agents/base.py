from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class AgentResult:
    """Saída padronizada de qualquer agente da esteira."""

    agent: str
    summary: str
    insights: list[str] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)
    recommendations: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class BaseAgent(ABC):
    """Contrato mínimo: nome + run(contexto) -> AgentResult."""

    name: str = "base"

    @abstractmethod
    def run(self, context: dict[str, Any]) -> AgentResult:
        raise NotImplementedError
