from __future__ import annotations

import os
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable, List, Dict, Any, Optional

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


@dataclass
class DocumentChunk:
    chunk_id: str
    source: str
    page: Optional[str]
    text: str
    start_char: int
    end_char: int

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class SimpleRAGPipeline:
    """Pipeline RAG simples e auditável.

    A implementação usa TF-IDF local para evitar dependência obrigatória de API externa,
    mas mantém a separação esperada em um pipeline RAG: carregar corpus, dividir em chunks,
    indexar, recuperar contexto e compor resposta.
    """

    def __init__(self, corpus_dir: str | os.PathLike, chunk_size: int = 900, overlap: int = 120):
        self.corpus_dir = Path(corpus_dir)
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.chunks: List[DocumentChunk] = []
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.matrix = None

    def load_documents(self) -> List[Dict[str, str]]:
        documents: List[Dict[str, str]] = []
        for path in sorted(self.corpus_dir.glob("**/*")):
            if path.is_file() and path.suffix.lower() in {".md", ".txt"}:
                text = path.read_text(encoding="utf-8")
                documents.append({"source": str(path.relative_to(self.corpus_dir)), "text": text})
        if not documents:
            raise FileNotFoundError(f"Nenhum arquivo .md/.txt encontrado em {self.corpus_dir}")
        return documents

    @staticmethod
    def _normalize_space(text: str) -> str:
        return re.sub(r"\n{3,}", "\n\n", text).strip()

    @staticmethod
    def _extract_page_label(text: str) -> Optional[str]:
        match = re.search(r"Página\s+(\d+)", text, flags=re.IGNORECASE)
        return match.group(1) if match else None

    def split_text(self, text: str, source: str) -> List[DocumentChunk]:
        """Divide por seções/páginas quando possível; senão usa janela deslizante."""
        text = self._normalize_space(text)
        sections = re.split(r"\n---\n", text)
        chunks: List[DocumentChunk] = []

        for section in sections:
            section = section.strip()
            if not section:
                continue
            page = self._extract_page_label(section)

            if len(section) <= self.chunk_size:
                idx = len(chunks)
                chunks.append(DocumentChunk(
                    chunk_id=f"{source}::chunk_{idx:04d}",
                    source=source,
                    page=page,
                    text=section,
                    start_char=0,
                    end_char=len(section),
                ))
                continue

            start = 0
            while start < len(section):
                end = min(start + self.chunk_size, len(section))
                window = section[start:end]
                # tenta quebrar no fim de frase para melhorar legibilidade
                if end < len(section):
                    last_period = max(window.rfind(". "), window.rfind("\n"))
                    if last_period > int(self.chunk_size * 0.6):
                        end = start + last_period + 1
                        window = section[start:end]
                idx = len(chunks)
                chunks.append(DocumentChunk(
                    chunk_id=f"{source}::chunk_{idx:04d}",
                    source=source,
                    page=page,
                    text=window.strip(),
                    start_char=start,
                    end_char=end,
                ))
                if end >= len(section):
                    break
                start = max(0, end - self.overlap)
        return chunks

    def build_index(self) -> "SimpleRAGPipeline":
        docs = self.load_documents()
        self.chunks = []
        for doc in docs:
            self.chunks.extend(self.split_text(doc["text"], doc["source"]))

        corpus_texts = [c.text for c in self.chunks]
        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            strip_accents="unicode",
            ngram_range=(1, 2),
            min_df=1,
            max_features=6000,
        )
        self.matrix = self.vectorizer.fit_transform(corpus_texts)
        return self

    def retrieve(self, query: str, k: int = 4) -> List[Dict[str, Any]]:
        if self.vectorizer is None or self.matrix is None:
            self.build_index()
        q_vec = self.vectorizer.transform([query])
        scores = cosine_similarity(q_vec, self.matrix).ravel()
        top_idx = np.argsort(scores)[::-1][:k]

        results: List[Dict[str, Any]] = []
        for rank, idx in enumerate(top_idx, start=1):
            chunk = self.chunks[int(idx)]
            results.append({
                **chunk.to_dict(),
                "rank": rank,
                "score": float(scores[int(idx)]),
            })
        return results

    def format_context(self, retrieved: Iterable[Dict[str, Any]], max_chars: int = 3500) -> str:
        pieces = []
        total = 0
        for item in retrieved:
            header = f"[Fonte: {item['source']} | página/seção: {item.get('page') or 'n/a'} | score: {item['score']:.3f}]"
            piece = header + "\n" + item["text"]
            if total + len(piece) > max_chars:
                break
            pieces.append(piece)
            total += len(piece)
        return "\n\n---\n\n".join(pieces)


def build_rag_pipeline(corpus_dir: str | os.PathLike = "data/corpus") -> SimpleRAGPipeline:
    return SimpleRAGPipeline(corpus_dir=corpus_dir).build_index()
