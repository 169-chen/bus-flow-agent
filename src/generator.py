"""答案生成：优先调用大模型 API（需 Key），否则用抽取式兜底。

设计要点（面试可讲）：
- Prompt 要求"仅依据参考资料作答 + 标注引用编号 + 无依据时明确拒答"
- 这是对"幻觉"的第一道防线，也是产品经理最该关注的 AI 产品设计点
"""
import json
import urllib.request
import urllib.error
from .config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL

SYSTEM_PROMPT = """你是"公交客流智能问答助手"，仅依据用户提供的【参考资料】回答问题。
规则：
1. 只使用参考资料中的信息，不得使用常识或自行编造，不得给出资料中没有的数字。
2. 每个结论后用 [编号] 标注来源，编号对应参考资料的序号。
3. 若参考资料不足以回答，直接回答"根据现有资料无法回答该问题"，并说明缺少什么信息。
4. 回答简洁，分点陈述，不要寒暄。"""


def _build_context(contexts):
    return "\n\n".join(
        f"[{i}]（来源：{c['doc_id']}）\n{c['text']}"
        for i, c in enumerate(contexts, 1)
    )


def generate_by_llm(question, contexts):
    """调用 OpenAI 兼容接口生成答案；失败时抛出异常，由上层兜底。"""
    user = f"【参考资料】\n{_build_context(contexts)}\n\n【问题】\n{question}"
    payload = {
        "model": LLM_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user},
        ],
        "temperature": 0.1,
    }
    req = urllib.request.Request(
        f"{LLM_BASE_URL}/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json",
                 "Authorization": f"Bearer {LLM_API_KEY}"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data["choices"][0]["message"]["content"].strip(), "大模型生成"


def _answerability(question, contexts, min_score=6.0):
    """可回答性检查：识别"知识库外"问题，防止 BM25 强行召回导致幻觉。

    规则（面试可讲）：
    1. 命中越界信号词（金额/未来预测/具体机构等，本知识库按设计不含此类
       信息）→ 直接拒答，不依赖检索得分。因为 BM25 会因"客流""数据"等
       通用词强行召回高分文档，得分不可信。
    2. 无信号但检索得分极低 → 拒答。
    """
    out_of_scope = ["万元", "亿元", "营收", "成本", "奖项", "团队", "成员",
                    "人数", "部署在", "预测", "未来", "精确到", "2024", "2025",
                    "具体通勤", "获得哪些"]
    has_signal = any(s in question for s in out_of_scope)
    weak_retrieval = not contexts or contexts[0].get("score", 0) < min_score
    return not (has_signal or weak_retrieval)


def generate_extractive(question, contexts):
    """无 API Key 时的抽取式兜底：挑出与问题最相关的原句并标注引用。"""
    if not contexts:
        return "根据现有资料无法回答该问题（知识库中未检索到相关内容）。", "抽取式兜底"
    if not _answerability(question, contexts):
        return ("根据现有知识库无法回答该问题：资料中未包含该问题涉及的"
                "具体信息，建议补充相关数据或文档后再提问。"), "拒答（可回答性检查）"
    # 抽取包含问题关键词的原句
    keywords = [w for w in _keywords(question) if len(w) >= 2]
    lines = []
    for i, c in enumerate(contexts, 1):
        for sentence in c["text"].replace("\n", " ").split("。"):
            s = sentence.strip().lstrip("# ").strip()
            if len(s) < 6 or s.startswith("-"):
                continue
            hits = sum(1 for w in keywords if w in s)
            if hits > 0:
                lines.append((hits, f"{s}。 [{i}]"))
    lines.sort(key=lambda x: x[0], reverse=True)
    if not lines:
        lines.append((0, f"{contexts[0]['text'][:120]}。 [1]"))
    answer = "\n".join(f"- {text}" for _, text in lines[:4])
    sources = "；".join(f"[{i}] {c['doc_id']}" for i, c in enumerate(contexts, 1))
    return f"根据知识库资料：\n{answer}\n\n来源：{sources}", "抽取式兜底"


def _keywords(question):
    from .retriever import tokenize
    return tokenize(question)


def generate(question, contexts):
    """统一入口：有 Key 走大模型，异常或无 Key 走抽取式兜底。"""
    if LLM_API_KEY:
        try:
            return generate_by_llm(question, contexts)
        except (urllib.error.URLError, KeyError, ValueError, OSError) as e:
            print(f"[warn] 大模型调用失败，切换抽取式兜底：{e}")
    return generate_extractive(question, contexts)
