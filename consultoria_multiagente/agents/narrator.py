from __future__ import annotations

from datetime import date
from typing import Any

from .base import AgentResult, BaseAgent


class NarratorAgent(BaseAgent):
    """Gera a narrativa comercial / one-pager da oferta.

    Transforma os outputs dos outros agentes em texto pronto para
    proposta, LinkedIn, landing ou pitch de 60 segundos.
    """

    name = "narrator"

    def run(self, context: dict[str, Any]) -> AgentResult:
        brand = context.get("brand", "Hermano Ramos · Consultoria")
        scout = context.get("scout", {})
        estimator = context.get("estimator", {})
        strategist = context.get("strategist", {})

        s_m = strategist.get("metrics", {})
        e_m = estimator.get("metrics", {})
        sc_m = scout.get("metrics", {})

        entry = s_m.get("entry_package", "diagnostico")
        entry_price = s_m.get("entry_price", 0)
        entry_hours = s_m.get("entry_hours", 0)
        icp = s_m.get("icp", {})
        positioning = s_m.get("positioning", "")
        pillars = s_m.get("pillars", [])
        ladder = s_m.get("ladder", [])

        one_pager = self._one_pager(
            brand=brand,
            icp=icp,
            positioning=positioning,
            pillars=pillars,
            entry=entry,
            entry_price=entry_price,
            entry_hours=entry_hours,
            ladder=ladder,
            scout_metrics=sc_m,
            estimator_metrics=e_m,
        )
        pitch_60s = self._pitch_60s(brand, positioning, entry, entry_price)
        linkedin = self._linkedin_post(brand, entry, entry_price, sc_m, e_m)

        return AgentResult(
            agent=self.name,
            summary="Narrativas comerciais geradas: one-pager, pitch 60s e post LinkedIn.",
            insights=[
                "One-pager pronto para PDF/Notion.",
                "Pitch de 60s para call ou vídeo curto.",
                "Post LinkedIn para atrair o ICP esta semana.",
            ],
            metrics={
                "one_pager": one_pager,
                "pitch_60s": pitch_60s,
                "linkedin_post": linkedin,
                "generated_on": date.today().isoformat(),
            },
            recommendations=[
                "Enviar o one-pager após a call de discovery.",
                "Gravar o pitch 60s e fixar no perfil.",
                "Publicar o post e responder comentários em <2h.",
            ],
        )

    def _one_pager(
        self,
        brand: str,
        icp: dict,
        positioning: str,
        pillars: list,
        entry: str,
        entry_price: float,
        entry_hours: float,
        ladder: list,
        scout_metrics: dict,
        estimator_metrics: dict,
    ) -> str:
        ladder_lines = "\n".join(
            f"  • {item.get('name', '').replace('_', ' ').title()}: "
            f"R$ {item.get('price', 0):,.0f} · {item.get('hours', 0):.0f}h — "
            f"{item.get('objetivo', '')}"
            for item in ladder
        )
        pillar_lines = "\n".join(f"  • {p}" for p in pillars)
        return f"""# {brand}
## Oferta multiagente · {date.today().strftime('%d/%m/%Y')}

### Para quem
{icp.get('label', 'Clientes B2B')}
_{icp.get('why', '')}_

### Promessa
{positioning}

### Como funciona (esteira)
1. **Scout** — qualifica o funil e acha leads quentes
2. **Estimator** — calcula faixas de preço e risco com o seu histórico
3. **Strategist** — empacota a escada de oferta
4. **Narrator** — escreve proposta, pitch e conteúdo

### Pilares
{pillar_lines}

### Escada comercial
{ladder_lines}

### Oferta de entrada sugerida
**{entry.replace('_', ' ').title()}** — R$ {entry_price:,.0f} · {entry_hours:.0f}h

### Prova a partir dos seus dados
- {scout_metrics.get('total_leads', 0)} leads no funil · maturidade {scout_metrics.get('maturity_score', 0)}/100
- {estimator_metrics.get('n_projects', 0)} projetos · ticket mediano R$ {estimator_metrics.get('median_price', 0):,.0f}
- {scout_metrics.get('hot_leads', 0)} leads quentes prontos para abordagem

### Próximo passo
Agendar diagnóstico (briefing de 5 perguntas) e sair com mapa + preço em até 7 dias.
"""

    def _pitch_60s(
        self, brand: str, positioning: str, entry: str, entry_price: float
    ) -> str:
        return (
            f"Eu sou {brand}. Ajudo times a transformar consultoria em sistema: "
            f"agentes especializados que qualificam leads, precificam projetos e "
            f"escrevem a oferta. {positioning} "
            f"Começamos pelo {entry.replace('_', ' ')} por cerca de R$ {entry_price:,.0f} — "
            f"você vê a esteira rodando nos seus dados ainda na primeira semana."
        )

    def _linkedin_post(
        self,
        brand: str,
        entry: str,
        entry_price: float,
        scout_metrics: dict,
        estimator_metrics: dict,
    ) -> str:
        return f"""Consultoria não escala no improviso.

Montei uma esteira multiagente com 4 papéis:
Scout (funil) → Estimator (preço) → Strategist (oferta) → Narrator (proposta).

Nos meus dados de demo:
• {scout_metrics.get('total_leads', 0)} leads · maturidade {scout_metrics.get('maturity_score', 0)}/100
• {estimator_metrics.get('n_projects', 0)} projetos · ticket mediano R$ {estimator_metrics.get('median_price', 0):,.0f}
• Entrada sugerida: {entry.replace('_', ' ')} ≈ R$ {entry_price:,.0f}

Se você vende serviço e quer repetibilidade sem perder o toque humano, DM aberta.

— {brand}
"""
