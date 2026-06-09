from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class RouteDecision:
    complexity: str
    model: str
    reason: str
    estimated_cost_usd: float


def classify_complexity(question: str) -> str:
    q = question.lower()
    complex_markers = [
        "compar", "estratégia", "arquitetura", "retenção", "incidente", "vazamento",
        "base legal", "posso armazenar", "como implementar", "fornecedor", "terceiro",
    ]
    if len(question) > 220 or any(m in q for m in complex_markers):
        return "complex"
    return "simple"


def route_question(question: str) -> RouteDecision:
    complexity = classify_complexity(question)
    cheap = os.getenv("CHEAP_MODEL", "gpt-4o-mini")
    premium = os.getenv("PREMIUM_MODEL", "gpt-4o")
    if complexity == "simple":
        return RouteDecision(
            complexity=complexity,
            model=cheap,
            reason="Pergunta curta/objetiva: rota cheap-first para reduzir custo.",
            estimated_cost_usd=0.00015,
        )
    return RouteDecision(
        complexity=complexity,
        model=premium,
        reason="Pergunta contextual/decisória: usa rota premium após retrieval e tools.",
        estimated_cost_usd=0.00120,
    )


def cost_saving_report(total_calls: int, cheap_calls: int, premium_calls: int) -> Dict[str, Any]:
    # valores ilustrativos para demonstrar cálculo no README/demo
    cheap_cost = 0.00015
    premium_cost = 0.00120
    actual = cheap_calls * cheap_cost + premium_calls * premium_cost
    baseline = total_calls * premium_cost
    saving = 0 if baseline == 0 else 1 - (actual / baseline)
    return {
        "total_calls": total_calls,
        "cheap_calls": cheap_calls,
        "premium_calls": premium_calls,
        "actual_cost_usd": round(actual, 6),
        "baseline_all_premium_usd": round(baseline, 6),
        "estimated_saving_pct": round(saving * 100, 2),
    }
