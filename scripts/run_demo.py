import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.pipeline.orchestrator import PortfolioAssistant
from src.pipeline.routing import cost_saving_report

questions = [
    "Posso armazenar CPF do cliente para emissão de nota fiscal?",
    "O que devo fazer se houve vazamento de dados pessoais? Cite o artigo 48.",
    "Quais cuidados devo ter ao usar logs com e-mail e IP para detectar fraude?",
]

assistant = PortfolioAssistant(corpus_dir=ROOT / "data" / "corpus")
results = []
for q in questions:
    r = assistant.answer(q)
    results.append({
        "question": q,
        "answer": r["answer"],
        "route": r["route"],
        "cache": r["cache"],
        "latency_ms": r["latency_ms"],
        "sources": r["sources"],
        "tool_calls": r["tool_calls"],
    })

# Repetição proposital para demonstrar exact cache
cached = assistant.answer(questions[0])

output = {
    "results": results,
    "cache_demo": {"question": questions[0], "cache": cached["cache"], "latency_ms": cached["latency_ms"]},
    "cache_report": assistant.cache.report(),
    "cost_report": cost_saving_report(
        total_calls=max(1, assistant.calls["cheap"] + assistant.calls["premium"]),
        cheap_calls=assistant.calls["cheap"],
        premium_calls=assistant.calls["premium"],
    ),
}
print(json.dumps(output, ensure_ascii=False, indent=2))
