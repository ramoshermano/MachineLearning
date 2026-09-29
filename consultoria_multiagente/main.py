#!/usr/bin/env python3
"""CLI da esteira multiagente de consultoria.

Uso:
  python main.py
  python main.py --brand "Sua Marca · Studio"
  python main.py --data-dir .. --output-dir ./outputs
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from pipeline import ConsultingPipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Roda Scout → Estimator → Strategist → Narrator nos CSVs do repo."
    )
    root = Path(__file__).resolve().parent
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=root.parent,
        help="Pasta com tracking.csv e projects.csv (default: raiz do repo).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=root / "outputs",
        help="Pasta de saída dos artefatos comerciais.",
    )
    parser.add_argument(
        "--brand",
        type=str,
        default="Hermano Ramos · Consultoria",
        help="Nome da marca na narrativa comercial.",
    )
    return parser


def print_console_brief(report: dict) -> None:
    results = report["results"]
    print("\n═══ ESTEIRA MULTIAGENTE DE CONSULTORIA ═══\n")
    for name in report["pipeline"]:
        block = results[name]
        print(f"▸ {name.upper()}")
        print(f"  {block['summary']}")
        for tip in block.get("recommendations", [])[:2]:
            print(f"  → {tip}")
        print()

    strategist = results["strategist"]["metrics"]
    print("═══ OFERTA ÂNCORA ═══")
    print(f"ICP: {strategist['icp']['label']}")
    print(f"Pacote: {strategist['entry_package']}")
    print(f"Preço: R$ {strategist['entry_price']:,.0f} · {strategist['entry_hours']:.0f}h")
    print(f"\n{strategist['positioning']}\n")


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    tracking = args.data_dir / "tracking.csv"
    projects = args.data_dir / "projects.csv"
    if not tracking.exists() or not projects.exists():
        print(
            f"CSVs não encontrados em {args.data_dir}. "
            "Espere tracking.csv e projects.csv.",
            file=sys.stderr,
        )
        return 1

    pipeline = ConsultingPipeline(data_dir=args.data_dir, brand=args.brand)
    report = pipeline.run()
    paths = ConsultingPipeline.save(report, args.output_dir)
    print_console_brief(report)
    print("Artefatos salvos:")
    for label, path in paths.items():
        print(f"  • {label}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
