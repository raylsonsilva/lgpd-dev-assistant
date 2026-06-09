from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from .cache import ExactAndSemanticCache
from .rag import build_rag_pipeline, SimpleRAGPipeline
from .routing import route_question
from .tools import infer_tool_calls, execute_tool_call, TOOL_SCHEMAS
from src.observability.trace import JsonlTracer


class OptionalLLMClient:
    """Cliente LLM opcional.

    Se OPENAI_API_KEY estiver configurada e o pacote openai instalado, usa a API.
    Caso contrário, gera resposta local baseada no contexto recuperado, suficiente para demo e smoke test.
    """

    def __init__(self):
        self.has_api = bool(os.getenv("OPENAI_API_KEY"))

    def generate(self, question: str, context: str, tool_results: List[Dict[str, Any]], model: str) -> str:
        if self.has_api:
            try:
                from openai import OpenAI
                client = OpenAI()
                messages = [
                    {
                        "role": "system",
                        "content": (
                            "Você é um assistente de compliance LGPD para desenvolvedores. "
                            "Responda em português, cite fontes do contexto e não dê parecer jurídico definitivo. "
                            "Se o contexto não sustentar a resposta, diga que não encontrou evidência suficiente."
                        ),
                    },
                    {
                        "role": "user",
                        "content": f"Pergunta: {question}\n\nContexto recuperado:\n{context}\n\nResultados de tools:\n{tool_results}",
                    },
                ]
                response = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=0.2,
                )
                return response.choices[0].message.content
            except Exception as exc:
                return self._fallback_answer(question, context, tool_results, f"Falha ao chamar LLM: {exc}")
        return self._fallback_answer(question, context, tool_results, None)

    @staticmethod
    def _fallback_answer(question: str, context: str, tool_results: List[Dict[str, Any]], warning: Optional[str]) -> str:
        lines = []
        if warning:
            lines.append(f"Observação técnica: {warning}")
        lines.append("Resposta gerada com base no corpus recuperado:")
        q = question.lower()

        if "vazamento" in q or "incidente" in q:
            lines.append(
                "Em caso de incidente ou vazamento, o caminho recomendado é conter o acesso, preservar evidências, "
                "identificar quais dados e titulares foram afetados, acionar o DPO/jurídico e avaliar comunicação à ANPD e aos titulares."
            )
        elif "cpf" in q or "armazenar" in q:
            lines.append(
                "O armazenamento de CPF pode ser permitido quando houver finalidade clara e base legal adequada, "
                "como obrigação legal ou execução de contrato, mas deve respeitar necessidade, retenção e segurança."
            )
        elif "excluir" in q or "eliminação" in q or "deletar" in q:
            lines.append(
                "Pedidos de exclusão devem ser avaliados conforme os direitos do titular; alguns dados podem ser eliminados, "
                "outros anonimizados ou mantidos quando houver obrigação legal ou necessidade legítima documentada."
            )
        else:
            lines.append(
                "A decisão deve considerar finalidade, base legal, minimização, transparência, segurança e registro das operações de tratamento."
            )

        if tool_results:
            lines.append("\nTools utilizadas:")
            for item in tool_results:
                if item.get("found") is True and "text" in item:
                    lines.append(f"- {item['text']}")
                elif "risk_level" in item:
                    lines.append(f"- Avaliação preliminar de risco: {item['risk_level']}. Ações: {', '.join(item['recommended_actions'][:3])}.")

        lines.append("\nFontes: trechos recuperados do corpus LGPD para desenvolvedores. Esta resposta não substitui validação jurídica/DPO.")
        return "\n".join(lines)


class PortfolioAssistant:
    def __init__(self, corpus_dir: str | os.PathLike = "data/corpus"):
        self.rag: SimpleRAGPipeline = build_rag_pipeline(corpus_dir)
        self.cache = ExactAndSemanticCache(ttl_seconds=3600, semantic_threshold=0.82)
        self.llm = OptionalLLMClient()
        self.tracer = JsonlTracer()
        self.calls = {"cheap": 0, "premium": 0}

    def answer(self, question: str, k: int = 4) -> Dict[str, Any]:
        start = time.time()
        cached = self.cache.get(question)
        if cached:
            cached["latency_ms"] = round((time.time() - start) * 1000, 2)
            self.tracer.log("cache_hit", {"question": question, "cache": cached.get("cache")})
            return cached

        route = route_question(question)
        if route.complexity == "simple":
            self.calls["cheap"] += 1
        else:
            self.calls["premium"] += 1

        retrieved = self.rag.retrieve(question, k=k)
        context = self.rag.format_context(retrieved)

        tool_calls = infer_tool_calls(question)
        tool_results = []
        for call in tool_calls:
            result = execute_tool_call(call)
            tool_results.append({"call": call, **result})

        final_answer = self.llm.generate(
            question=question,
            context=context,
            tool_results=tool_results,
            model=route.model,
        )

        response = {
            "question": question,
            "answer": final_answer,
            "sources": [
                {
                    "source": r["source"],
                    "page": r.get("page"),
                    "score": round(r["score"], 4),
                    "chunk_id": r["chunk_id"],
                    "preview": r["text"][:260].replace("\n", " ") + "...",
                }
                for r in retrieved
            ],
            "tool_calls": tool_calls,
            "tool_results": tool_results,
            "route": {
                "complexity": route.complexity,
                "model": route.model,
                "reason": route.reason,
                "estimated_cost_usd": route.estimated_cost_usd,
            },
            "cache": {"hit": False, "type": "miss"},
            "latency_ms": round((time.time() - start) * 1000, 2),
            "tool_schemas": TOOL_SCHEMAS,
        }
        self.cache.set(question, response)
        self.tracer.log("answer", {"question": question, "route": response["route"], "latency_ms": response["latency_ms"]})
        return response
