from pathlib import Path

from src.pipeline.orchestrator import PortfolioAssistant


def test_pipeline_responde_com_fontes_e_tool():
    root = Path(__file__).resolve().parents[1]
    assistant = PortfolioAssistant(corpus_dir=root / "data" / "corpus")
    result = assistant.answer("Posso armazenar CPF do cliente para emissão de nota fiscal?")
    assert result["answer"]
    assert len(result["sources"]) >= 1
    assert any(call["name"] == "assess_lgpd_risk" for call in result["tool_calls"])


def test_cache_exact_hit():
    root = Path(__file__).resolve().parents[1]
    assistant = PortfolioAssistant(corpus_dir=root / "data" / "corpus")
    q = "O que devo fazer se houve vazamento de dados pessoais?"
    assistant.answer(q)
    second = assistant.answer(q)
    assert second["cache"]["hit"] is True
