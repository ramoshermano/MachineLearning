from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from .base import AgentResult, BaseAgent


class ScoutAgent(BaseAgent):
    """Qualifica o funil comercial a partir de tracking.csv.

    Interpreta o caminho do lead (inicial → palestras/contato → compra/patrocínio)
    e devolve um score de maturidade da demanda + segmentos hot/warm/cold.
    """

    name = "scout"

    def __init__(self, tracking_path: Path) -> None:
        self.tracking_path = tracking_path

    def run(self, context: dict[str, Any]) -> AgentResult:
        df = pd.read_csv(self.tracking_path)
        total = len(df)
        if total == 0:
            return AgentResult(
                agent=self.name,
                summary="Funil vazio — sem leads para qualificar.",
                recommendations=[
                    "Ativar captura mínima (formulário + palestra) antes de escalar agentes."
                ],
            )

        bought = int(df["comprou"].sum())
        sponsor = int(df["patrocinio"].sum())
        contacted = int(df["contato"].sum())
        lectures = int(df["palestras"].sum())
        started = int(df["inicial"].sum())

        conversion = bought / total
        contact_rate = contacted / total
        lecture_rate = lectures / total
        sponsor_rate = sponsor / total

        # Segmentação simples e vendável em demo
        hot = df[(df["contato"] == 1) & (df["comprou"] == 0)]
        warm = df[(df["palestras"] == 1) & (df["contato"] == 0) & (df["comprou"] == 0)]
        cold = df[(df["inicial"] == 1) & (df["palestras"] == 0) & (df["contato"] == 0)]
        champions = df[(df["comprou"] == 1) | (df["patrocinio"] == 1)]

        maturity = min(
            100.0,
            round(
                (conversion * 40)
                + (contact_rate * 25)
                + (lecture_rate * 20)
                + (sponsor_rate * 15)
                + 10,
                1,
            ),
        )

        insights = [
            f"{total} leads no funil; conversão atual {conversion:.1%}.",
            f"{len(hot)} leads quentes (contato sem compra) — prioridade de follow-up.",
            f"{len(warm)} leads mornos (palestra sem contato).",
            f"{len(champions)} clientes/patrocinadores ativos para prova social.",
        ]

        recommendations = []
        if len(hot) > 0:
            recommendations.append(
                f"Rodar sequência de fechamento em {len(hot)} leads quentes esta semana."
            )
        if conversion < 0.15:
            recommendations.append(
                "Oferta ainda fricciona: empacotar diagnóstico pago antes do projeto full."
            )
        if lecture_rate > contact_rate:
            recommendations.append(
                "Palestras geram volume — criar CTA de diagnóstico no fim de cada sessão."
            )
        if not recommendations:
            recommendations.append(
                "Funil saudável: escalar aquisição mantendo o mesmo playbook de contato."
            )

        return AgentResult(
            agent=self.name,
            summary=(
                f"Maturidade do funil: {maturity}/100. "
                f"Início={started}, palestras={lectures}, contato={contacted}, "
                f"compra={bought}, patrocínio={sponsor}."
            ),
            insights=insights,
            metrics={
                "total_leads": total,
                "conversion_rate": round(conversion, 4),
                "contact_rate": round(contact_rate, 4),
                "lecture_rate": round(lecture_rate, 4),
                "sponsor_rate": round(sponsor_rate, 4),
                "maturity_score": maturity,
                "hot_leads": int(len(hot)),
                "warm_leads": int(len(warm)),
                "cold_leads": int(len(cold)),
                "champions": int(len(champions)),
            },
            recommendations=recommendations,
        )
