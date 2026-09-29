from __future__ import annotations

from typing import Any

from .base import AgentResult, BaseAgent


class StrategistAgent(BaseAgent):
    """Empacota a oferta de consultoria multiagente.

    Combina maturidade do funil (Scout) + pricing (Estimator) em um
    posicionamento comercial claro: para quem, o quê, como e por quê agora.
    """

    name = "strategist"

    OFFER_PILLARS = (
        "Descoberta orientada a dados (funil + histórico de projetos)",
        "Esteira multiagente com papéis claros e handoff",
        "Entrega demoável em semanas, não meses",
        "Playbooks reutilizáveis para o time do cliente",
    )

    def run(self, context: dict[str, Any]) -> AgentResult:
        scout = context.get("scout", {})
        estimator = context.get("estimator", {})
        scout_m = scout.get("metrics", {})
        est_m = estimator.get("metrics", {})

        entry = est_m.get("entry_package", "diagnostico")
        packages = est_m.get("packages", {})
        entry_pkg = packages.get(entry, {})
        hot = scout_m.get("hot_leads", 0)
        maturity = scout_m.get("maturity_score", 50)
        conversion = scout_m.get("conversion_rate", 0)

        icp = self._icp(maturity, conversion)
        positioning = self._positioning(entry)
        proof = self._proof_points(scout_m, est_m)
        next_moves = self._next_moves(entry, hot, packages)

        insights = [
            f"ICP prioritário: {icp['label']} — {icp['why']}",
            f"Posicionamento: {positioning}",
            f"Prova social interna: {proof}",
            f"Movimento comercial imediato: {next_moves[0]}",
        ]

        recommendations = [
            f"Abrir conversas com oferta âncora: {entry} "
            f"(R$ {entry_pkg.get('preco', 0):,.0f}).",
            "Na call, mostrar a esteira Scout → Estimator → Strategist → Narrator ao vivo.",
            "Fechar diagnóstico pago em 48h com briefing de 5 perguntas.",
            "Upsell natural: cada pacote desbloqueia o seguinte com crédito parcial.",
        ]

        return AgentResult(
            agent=self.name,
            summary=(
                f"Oferta {entry} para {icp['label']}. "
                f"Âncora R$ {entry_pkg.get('preco', 0):,.0f} — {entry_pkg.get('objetivo', '')}"
            ),
            insights=insights,
            metrics={
                "icp": icp,
                "positioning": positioning,
                "pillars": list(self.OFFER_PILLARS),
                "entry_package": entry,
                "entry_price": entry_pkg.get("preco"),
                "entry_hours": entry_pkg.get("horas"),
                "ladder": [
                    {
                        "name": name,
                        "price": pkg.get("preco"),
                        "hours": pkg.get("horas"),
                        "objetivo": pkg.get("objetivo"),
                    }
                    for name, pkg in packages.items()
                ],
                "next_moves": next_moves,
                "proof": proof,
            },
            recommendations=recommendations,
        )

    def _icp(self, maturity: float, conversion: float) -> dict[str, str]:
        if maturity >= 70 and conversion >= 0.2:
            return {
                "label": "PMEs com funil aquecido e time lean",
                "why": "Já compram; precisam de velocidade de entrega e diferenciação.",
            }
        if maturity >= 40:
            return {
                "label": "Consultorias e studios que querem produto AI-led",
                "why": "Têm demanda, mas falta sistema repetível de discovery → proposta.",
            }
        return {
            "label": "Fundadores B2B em validação de oferta",
            "why": "Precisam de diagnóstico barato e narrativa clara antes de escalar.",
        }

    def _positioning(self, entry: str) -> str:
        map_ = {
            "diagnostico": (
                "Consultoria de descoberta com agentes: em dias você sai com "
                "mapa de funil, faixas de preço e script de oferta."
            ),
            "sprint_mvp": (
                "Sprint multiagente: da dor do cliente a um piloto rodando "
                "com papéis claros e métricas de negócio."
            ),
            "programa_completo": (
                "Programa de implantação: esteira multiagente + playbooks "
                "comerciais + handoff para o time interno."
            ),
        }
        return map_.get(entry, map_["diagnostico"])

    def _proof_points(self, scout_m: dict, est_m: dict) -> str:
        return (
            f"{scout_m.get('total_leads', 0)} leads analisados, "
            f"{est_m.get('n_projects', 0)} projetos no histórico de pricing, "
            f"ticket mediano R$ {est_m.get('median_price', 0):,.0f}."
        )

    def _next_moves(self, entry: str, hot: int, packages: dict) -> list[str]:
        moves = []
        if hot > 0:
            moves.append(
                f"Contatar {min(hot, 10)} leads quentes com a oferta {entry}."
            )
        sprint = packages.get("sprint_mvp", {})
        full = packages.get("programa_completo", {})
        moves.append(
            f"Na proposta, mostrar escada: Diagnóstico → Sprint "
            f"(R$ {sprint.get('preco', 0):,.0f}) → Programa "
            f"(R$ {full.get('preco', 0):,.0f})."
        )
        moves.append(
            "Publicar um case curto da demo (antes/depois do funil) no portfólio."
        )
        return moves
