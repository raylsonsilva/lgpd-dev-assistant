from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

# Permite executar via streamlit run src/ui/streamlit_app.py
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.pipeline.orchestrator import PortfolioAssistant
from src.pipeline.routing import cost_saving_report


st.set_page_config(page_title="LGPD Dev Assistant", page_icon="🛡️", layout="wide")

st.title("🛡️ LGPD Dev Assistant")
st.caption("Assistente RAG + tool-use para apoiar decisões de privacidade em projetos de software.")


@st.cache_resource
def load_assistant():
    corpus_dir = ROOT / "data" / "corpus"
    return PortfolioAssistant(corpus_dir=corpus_dir)


assistant = load_assistant()

with st.sidebar:
    st.header("Configuração")
    st.write("Corpus: `data/corpus/lgpd_corpus_dev.md`")
    st.write("RAG: TF-IDF local auditável")
    st.write("Tools: `cite_article`, `assess_lgpd_risk`")
    st.write("Cache TTL: 1h")
    st.divider()
    if st.button("Limpar conversa"):
        st.session_state.messages = []
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Olá! Pergunte algo sobre LGPD aplicada a sistemas, por exemplo: 'Posso armazenar CPF para emissão de nota fiscal?'",
        }
    ]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

examples = [
    "Posso armazenar CPF do cliente para emissão de nota fiscal?",
    "O que devo fazer se houve vazamento de dados pessoais?",
    "Quais cuidados devo ter ao usar logs com e-mail e IP?",
]

st.write("Exemplos rápidos:")
cols = st.columns(3)
for col, ex in zip(cols, examples):
    if col.button(ex):
        st.session_state["pending_question"] = ex
        st.rerun()

prompt = st.chat_input("Digite sua pergunta sobre LGPD e desenvolvimento...")
if not prompt and "pending_question" in st.session_state:
    prompt = st.session_state.pop("pending_question")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Consultando corpus, tools e cache..."):
            result = assistant.answer(prompt)
        st.markdown(result["answer"])

        with st.expander("Fontes recuperadas"):
            for src in result["sources"]:
                st.markdown(f"**{src['source']} — página/seção {src.get('page') or 'n/a'}** | score `{src['score']}`")
                st.write(src["preview"])

        with st.expander("Detalhes técnicos"):
            st.json({
                "route": result["route"],
                "cache": result["cache"],
                "tool_calls": result["tool_calls"],
                "latency_ms": result["latency_ms"],
                "cache_report": assistant.cache.report(),
            })

    st.session_state.messages.append({"role": "assistant", "content": result["answer"]})

st.divider()
report = cost_saving_report(
    total_calls=max(1, assistant.calls["cheap"] + assistant.calls["premium"]),
    cheap_calls=assistant.calls["cheap"],
    premium_calls=assistant.calls["premium"],
)
st.caption(f"Estimativa de custo/routing: {report}")
