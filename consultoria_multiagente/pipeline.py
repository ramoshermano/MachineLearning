from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from agents import EstimatorAgent, NarratorAgent, ScoutAgent, StrategistAgent


class ConsultingPipeline:
    """Orquestra Scout → Estimator → Strategist → Narrator.

    Cada agente recebe o contexto acumulado e devolve um AgentResult.
    O resultado final é um briefing comercial pronto para demo/proposta.
    """

    def __init__(
        self,
        data_dir: Path,
        brand: str = "Hermano Ramos · Consultoria",
    ) -> None:
        self.data_dir = data_dir
        self.brand = brand
        self.scout = ScoutAgent(data_dir / "tracking.csv")
        self.estimator = EstimatorAgent(data_dir / "projects.csv")
        self.strategist = StrategistAgent()
        self.narrator = NarratorAgent()

    def run(self) -> dict[str, Any]:
        context: dict[str, Any] = {"brand": self.brand}

        scout_result = self.scout.run(context)
        context["scout"] = scout_result.to_dict()

        estimator_result = self.estimator.run(context)
        context["estimator"] = estimator_result.to_dict()

        strategist_result = self.strategist.run(context)
        context["strategist"] = strategist_result.to_dict()

        narrator_result = self.narrator.run(context)
        context["narrator"] = narrator_result.to_dict()

        return {
            "brand": self.brand,
            "pipeline": ["scout", "estimator", "strategist", "narrator"],
            "results": {
                "scout": context["scout"],
                "estimator": context["estimator"],
                "strategist": context["strategist"],
                "narrator": context["narrator"],
            },
        }

    @staticmethod
    def save(report: dict[str, Any], output_dir: Path) -> dict[str, Path]:
        output_dir.mkdir(parents=True, exist_ok=True)
        paths: dict[str, Path] = {}

        json_path = output_dir / "relatorio_multiagente.json"
        json_path.write_text(
            json.dumps(report, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        paths["json"] = json_path

        one_pager = (
            report.get("results", {})
            .get("narrator", {})
            .get("metrics", {})
            .get("one_pager", "")
        )
        md_path = output_dir / "one_pager_oferta.md"
        md_path.write_text(one_pager, encoding="utf-8")
        paths["one_pager"] = md_path

        pitch = (
            report.get("results", {})
            .get("narrator", {})
            .get("metrics", {})
            .get("pitch_60s", "")
        )
        linkedin = (
            report.get("results", {})
            .get("narrator", {})
            .get("metrics", {})
            .get("linkedin_post", "")
        )
        copy_path = output_dir / "copys_comerciais.md"
        copy_path.write_text(
            f"## Pitch 60s\n\n{pitch}\n\n## Post LinkedIn\n\n{linkedin}\n",
            encoding="utf-8",
        )
        paths["copys"] = copy_path
        return paths
