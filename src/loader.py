"""文档加载与切分：把 data/knowledge 下的 Markdown 切成可检索的文本块。"""
import re
from pathlib import Path
from .config import KB_DIR, CHUNK_SIZE, CHUNK_OVERLAP


def load_documents(kb_dir: Path = KB_DIR):
    """读取知识库目录下所有 .md 文件，返回 [{doc_id, text}]。"""
    docs = []
    for path in sorted(Path(kb_dir).rglob("*.md")):
        text = path.read_text(encoding="utf-8", errors="ignore")
        docs.append({"doc_id": path.stem, "text": text})
    return docs


def split_text(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP):
    """按段落优先、超长段落再按字符滑窗切分。"""
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    chunks, buf = [], ""
    for para in paragraphs:
        if len(buf) + len(para) + 1 <= size:
            buf = (buf + "\n" + para).strip()
        else:
            if buf:
                chunks.append(buf)
            if len(para) <= size:
                buf = para
            else:
                step = size - overlap
                for i in range(0, len(para), step):
                    chunks.append(para[i:i + size])
                buf = ""
    if buf:
        chunks.append(buf)
    return chunks


def build_chunks(docs):
    """把所有文档切成带来源标记的文本块。"""
    chunks = []
    for doc in docs:
        for i, piece in enumerate(split_text(doc["text"])):
            chunks.append({
                "chunk_id": f'{doc["doc_id"]}#{i}',
                "doc_id": doc["doc_id"],
                "text": piece,
            })
    return chunks


if __name__ == "__main__":
    d = load_documents()
    c = build_chunks(d)
    print(f"加载文档 {len(d)} 篇，切分文本块 {len(c)} 个")
    for x in c[:3]:
        print(f'  {x["chunk_id"]}: {x["text"][:50]}...')
