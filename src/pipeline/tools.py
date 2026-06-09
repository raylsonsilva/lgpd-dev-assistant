from __future__ import annotations

import re
from typing import Dict, Any, Callable


ARTICLE_SUMMARIES: Dict[int, str] = {
    5: "Art. 5º — define conceitos como dado pessoal, dado pessoal sensível, dado anonimizado, controlador, operador e encarregado.",
    6: "Art. 6º — estabelece princípios como finalidade, adequação, necessidade, transparência, segurança, prevenção e responsabilização.",
    7: "Art. 7º — lista bases legais para tratamento de dados pessoais comuns, como consentimento, obrigação legal, execução de contrato e legítimo interesse.",
    11: "Art. 11 — trata das hipóteses para tratamento de dados pessoais sensíveis, exigindo cuidado reforçado.",
    18: "Art. 18 — descreve direitos do titular, como acesso, correção, eliminação, portabilidade e informação sobre compartilhamento.",
    37: "Art. 37 — orienta a manutenção de registros das operações de tratamento de dados pessoais.",
    46: "Art. 46 — exige medidas de segurança técnicas e administrativas para proteger dados pessoais.",
    48: "Art. 48 — trata de comunicação de incidentes de segurança que possam gerar risco ou dano relevante aos titulares.",
}


def cite_article(article_number: int) -> Dict[str, Any]:
    """Retorna resumo auditável de um artigo LGPD usado como tool customizada."""
    text = ARTICLE_SUMMARIES.get(int(article_number))
    if not text:
        return {
            "found": False,
            "article": int(article_number),
            "text": "Artigo não encontrado no corpus resumido do projeto.",
            "recommendation": "Consultar texto oficial da LGPD ou ampliar o corpus.",
        }
    return {
        "found": True,
        "article": int(article_number),
        "text": text,
        "recommendation": "Usar este artigo como referência inicial e validar com o DPO/jurídico em caso real.",
    }


def assess_lgpd_risk(data_type: str, purpose: str, is_sensitive: bool = False, has_consent: bool = False) -> Dict[str, Any]:
    """Classifica risco preliminar de tratamento de dados para apoiar a resposta do assistente."""
    text = f"{data_type} {purpose}".lower()
    sensitive_terms = ["saúde", "saude", "biometr", "relig", "racial", "criança", "crianca", "menor", "genético", "genetico"]
    personal_terms = ["cpf", "email", "e-mail", "telefone", "ip", "endereço", "endereco", "nome"]

    detected_sensitive = is_sensitive or any(t in text for t in sensitive_terms)
    detected_personal = detected_sensitive or any(t in text for t in personal_terms)

    if detected_sensitive:
        level = "alto"
        actions = [
            "Validar base legal específica para dado sensível.",
            "Aplicar acesso restrito, criptografia e auditoria.",
            "Evitar uso em ambiente de teste sem anonimização.",
        ]
    elif detected_personal:
        level = "médio"
        actions = [
            "Confirmar finalidade e base legal antes da coleta.",
            "Coletar somente o mínimo necessário.",
            "Definir retenção e controles de acesso.",
        ]
    else:
        level = "baixo"
        actions = [
            "Confirmar se o dado é realmente anônimo.",
            "Documentar a finalidade do tratamento.",
        ]

    if "marketing" in text and not has_consent:
        level = "alto" if level == "médio" else level
        actions.append("Revisar consentimento ou legítimo interesse para uso em marketing.")

    return {
        "risk_level": level,
        "detected_personal_data": detected_personal,
        "detected_sensitive_data": detected_sensitive,
        "suggested_articles": [5, 6, 7, 11 if detected_sensitive else 18, 46],
        "recommended_actions": actions,
    }


TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "cite_article",
            "description": "Retorna resumo auditável de um artigo da LGPD disponível no corpus do projeto.",
            "parameters": {
                "type": "object",
                "properties": {
                    "article_number": {
                        "type": "integer",
                        "description": "Número do artigo da LGPD. Exemplos: 5, 6, 7, 18, 37, 46, 48.",
                    }
                },
                "required": ["article_number"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "assess_lgpd_risk",
            "description": "Classifica risco preliminar de tratamento de dados pessoais em um cenário de software.",
            "parameters": {
                "type": "object",
                "properties": {
                    "data_type": {"type": "string", "description": "Tipo de dado tratado. Ex.: CPF, e-mail, dado de saúde."},
                    "purpose": {"type": "string", "description": "Finalidade do tratamento."},
                    "is_sensitive": {"type": "boolean", "description": "Indica se envolve dado sensível."},
                    "has_consent": {"type": "boolean", "description": "Indica se há consentimento explícito."},
                },
                "required": ["data_type", "purpose"],
            },
        },
    },
]


TOOL_REGISTRY: Dict[str, Callable[..., Dict[str, Any]]] = {
    "cite_article": cite_article,
    "assess_lgpd_risk": assess_lgpd_risk,
}


def infer_tool_calls(question: str) -> list[dict[str, Any]]:
    """Heurística auditável para demonstrar tool-use mesmo sem API LLM."""
    calls = []
    for match in re.finditer(r"art(?:igo|\.)?\s*(\d{1,2})", question.lower()):
        calls.append({"name": "cite_article", "arguments": {"article_number": int(match.group(1))}})

    if any(term in question.lower() for term in ["cpf", "e-mail", "email", "saúde", "saude", "biometr", "vazamento", "incidente", "marketing", "logs", "ip"]):
        calls.append({
            "name": "assess_lgpd_risk",
            "arguments": {
                "data_type": question[:120],
                "purpose": question[:180],
                "is_sensitive": any(t in question.lower() for t in ["saúde", "saude", "biometr"]),
                "has_consent": "consentimento" in question.lower(),
            },
        })
    return calls


def execute_tool_call(call: Dict[str, Any]) -> Dict[str, Any]:
    name = call["name"]
    args = call.get("arguments", {})
    if name not in TOOL_REGISTRY:
        return {"error": f"Tool {name} não registrada."}
    return TOOL_REGISTRY[name](**args)
