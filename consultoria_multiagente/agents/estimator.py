from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from .base import AgentResult, BaseAgent


class EstimatorAgent(BaseAgent):
    """Estima preço e risco de projeto a partir de projects.csv.

    Usa estatísticas do histórico (horas × preço × taxa de não-finalização)
    para sugerir faixas comerciais e um ticket-alvo para a oferta.
    """

    name = "estimator"

    def __init__(self, projects_path: Path) -> None:
        self.projects_path = projects_path

    def run(self, context: dict[str, Any]) -> AgentResult:
        df = pd.read_csv(self.projects_path)
        finished = df[df["nao_finalizado"] == 0].copy()
        unfinished = df[df["nao_finalizado"] == 1].copy()

        # Base: projetos finalizados com horas > 0
        priced = finished[finished["horas_esperadas"] > 0].copy()
        if priced.empty:
            priced = df[df["horas_esperadas"] > 0].copy()

        priced["preco_hora"] = priced["preco"] / priced["horas_esperadas"]

        # Remove cauda barata (ruído / jobs de commodity) para ancorar oferta premium
        rate_floor = float(priced["preco_hora"].quantile(0.40))
        commercial = priced[priced["preco_hora"] >= rate_floor].copy()
        if commercial.empty:
            commercial = priced

        median_hours = float(commercial["horas_esperadas"].median())
        median_price = float(commercial["preco"].median())
        median_rate = float(commercial["preco_hora"].median())
        # Piso comercial mínimo para consultoria (evita ticket ridículo em demos)
        consulting_floor = 120.0
        sell_rate = max(median_rate, consulting_floor)
        p25_price = float(commercial["preco"].quantile(0.25))
        p75_price = float(commercial["preco"].quantile(0.75))
        risk_rate = float(df["nao_finalizado"].mean())

        # Pacotes no formato de oferta (não cópia literal do ticket mediano)
        discovery_hours = 12.0
        sprint_hours = 40.0
        full_hours = max(80.0, round(median_hours * 1.1, 0))

        packages = {
            "diagnostico": {
                "horas": discovery_hours,
                "preco": round(discovery_hours * sell_rate, 0),
                "objetivo": "Mapear dor, dados e quick wins em 1–2 semanas.",
            },
            "sprint_mvp": {
                "horas": sprint_hours,
                "preco": round(sprint_hours * sell_rate, 0),
                "objetivo": "Entregar um piloto multiagente utilizável pelo time.",
            },
            "programa_completo": {
                "horas": full_hours,
                "preco": round(full_hours * sell_rate * (1 + risk_rate * 0.25), 0),
                "objetivo": "Implantar esteira + playbooks + handoff operacional.",
            },
        }

        # Ajuste pelo funil (se Scout já rodou)
        scout = context.get("scout", {})
        maturity = scout.get("metrics", {}).get("maturity_score", 50)
        if maturity < 40:
            entry = "diagnostico"
            rationale = "Funil imaturo: entrada baixa reduz risco e gera prova."
        elif maturity < 70:
            entry = "sprint_mvp"
            rationale = "Funil em aquecimento: sprint prova valor e abre upsell."
        else:
            entry = "programa_completo"
            rationale = "Funil maduro: vender programa completo com ancoragem nos pacotes."

        target = packages[entry]

        insights = [
            f"Ticket mediano (faixa comercial): R$ {median_price:,.0f} em ~{median_hours:.0f}h "
            f"(≈ R$ {median_rate:,.0f}/h histórico; taxa de venda R$ {sell_rate:,.0f}/h).",
            f"Faixa interquartil de preço: R$ {p25_price:,.0f} – R$ {p75_price:,.0f}.",
            f"Taxa de não-finalização: {risk_rate:.1%} — embutir margem de risco no full.",
            f"Pacote de entrada sugerido: {entry} (R$ {target['preco']:,.0f}).",
        ]

        recommendations = [
            rationale,
            "Ancorar proposta mostrando Diagnóstico → Sprint → Programa.",
            "Condicionar desconto a escopo fechado e critérios de aceite claros.",
        ]
        if risk_rate > 0.35:
            recommendations.append(
                "Histórico de abandono alto: milestone payments e kickoff pago obrigatório."
            )

        return AgentResult(
            agent=self.name,
            summary=(
                f"Taxa de venda R$ {sell_rate:,.0f}/h (histórico mediano R$ {median_rate:,.0f}/h). "
                f"Entrada recomendada: {entry} (R$ {target['preco']:,.0f} / {target['horas']:.0f}h)."
            ),
            insights=insights,
            metrics={
                "n_projects": int(len(df)),
                "n_finished": int(len(finished)),
                "n_unfinished": int(len(unfinished)),
                "median_hours": round(median_hours, 1),
                "median_price": round(median_price, 2),
                "median_hourly_rate": round(median_rate, 2),
                "sell_hourly_rate": round(sell_rate, 2),
                "price_p25": round(p25_price, 2),
                "price_p75": round(p75_price, 2),
                "unfinished_rate": round(risk_rate, 4),
                "entry_package": entry,
                "packages": packages,
            },
            recommendations=recommendations,
        )
