"""RAG 管线：加载 -> 切分 -> 检索 -> 生成，对外只暴露 ask()。"""
from .config import TOP_K
from .loader import load_documents, build_chunks
from .retriever import BM25Retriever
from .generator import generate


class RAGPipeline:
    def __init__(self, kb_dir=None):
        docs = load_documents() if kb_dir is None else load_documents(kb_dir)
        self.chunks = build_chunks(docs)
        self.retriever = BM25Retriever(self.chunks)
        self.docs = docs

    def ask(self, question, top_k=TOP_K):
        contexts = self.retriever.retrieve(question, top_k)
        answer, mode = generate(question, contexts)
        return {
            "question": question,
            "answer": answer,
            "mode": mode,
            "contexts": contexts,
        }
