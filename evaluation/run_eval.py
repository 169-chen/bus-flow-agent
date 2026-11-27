"""评测脚本：跑测试集，计算检索命中率/准确率/幻觉率，输出 Markdown 报告。

这是本项目最体现"AI 产品经理"能力的部分：
- 定义评测维度（检索 vs 生成分开看，便于定位问题）
- 错误归因（是检索没召回，还是生成没遵循资料）
- 把"效果好不好"变成可量化的数字
"""
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.config import TESTSET_PATH, REPORT_DIR, TOP_K
from src.pipeline import RAGPipeline


def hit_at_k(retrieved_docs, expected_doc, k=TOP_K):
    return 1 if expected_doc in retrieved_docs[:k] else 0


def answer_correct(answer, keywords):
    """关键词覆盖率近似判断答案是否命中要点（>=60% 算正确）。"""
    if not keywords:
        return 0
    hits = sum(1 for w in keywords if w in answer)
    return 1 if hits / len(keywords) >= 0.6 else 0


def refusal_correct(answer):
    """拒答题：答案明确说无法回答才算正确。"""
    markers = ["无法回答", "没有", "不包含", "无法", "未提及", "不足"]
    return 1 if any(m in answer for m in markers) else 0


def run():
    testset = json.loads(TESTSET_PATH.read_text(encoding="utf-8"))
    pipe = RAGPipeline()

    stats = {"total": 0, "hit": 0, "correct": 0, "refuse_ok": 0,
             "refuse_total": 0, "answer_total": 0}
    details = []

    for case in testset:
        result = pipe.ask(case["question"])
        retrieved = [c["doc_id"] for c in result["contexts"]]
        h = hit_at_k(retrieved, case["expected_doc"])
        stats["hit"] += h

        if case["type"] == "拒答题":
            ok = refusal_correct(result["answer"])
            stats["refuse_ok"] += ok
            stats["refuse_total"] += 1
        else:
            ok = answer_correct(result["answer"], case.get("keywords", []))
            stats["correct"] += ok
            stats["answer_total"] += 1

        stats["total"] += 1
        details.append({
            "id": case["id"],
            "question": case["question"],
            "type": case["type"],
            "expected_doc": case["expected_doc"],
            "retrieved": retrieved,
            "hit": h,
            "ok": ok,
            "answer": result["answer"],
        })

    hit_rate = stats["hit"] / stats["total"]
    acc = stats["correct"] / max(stats["answer_total"], 1)
    refuse_rate = stats["refuse_ok"] / max(stats["refuse_total"], 1)

    lines = [
        "# 评测报告",
        f"> 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"> 测试集规模：{stats['total']} 题｜检索 Top-K：{TOP_K}",
        "",
        "## 一、核心指标",
        "",
        "| 指标 | 数值 | 说明 |",
        "|---|---|---|",
        f"| 检索命中率 Recall@{TOP_K} | {hit_rate:.0%} | 正确文档是否进入 Top-{TOP_K} 召回 |",
        f"| 答案要点准确率 | {acc:.0%} | 关键词覆盖率 ≥60% 判为正确 |",
        f"| 拒答准确率 | {refuse_rate:.0%} | 知识库外问题能否正确拒答 |",
        f"| 幻觉风险（估算） | {(1-refuse_rate):.0%} | 1 - 拒答准确率，越低越好 |",
        "",
        "## 二、错误归因",
        "",
    ]
    retr_err = [d for d in details if not d["hit"]]
    gen_err = [d for d in details if d["hit"] and not d["ok"]]
    lines += [
        f"- **检索层问题**：{len(retr_err)} 题未召回正确文档 → 需优化分块大小 / 召回策略。",
        f"- **生成层问题**：{len(gen_err)} 题召回正确但答错 → 需优化 Prompt 约束。",
        "",
        "## 三、失败样例",
        "",
    ]
    for d in (retr_err + gen_err)[:5]:
        lines += [
            f"**#{d['id']} {d['question']}**（{d['type']}）",
            f"- 期望来源：{d['expected_doc']}｜实际召回：{d['retrieved'] or '无'}",
            f"- 回答：{d['answer'][:120]}",
            "",
        ]
    lines += ["## 四、逐题明细", "", "| ID | 问题 | 类型 | 命中 | 判定 |", "|---|---|---|---|---|"]
    for d in details:
        lines.append(f"| {d['id']} | {d['question']} | {d['type']} | {'✓' if d['hit'] else '✗'} | {'✓' if d['ok'] else '✗'} |")

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORT_DIR / "eval_report.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")

    print(f"评测完成：{stats['total']} 题")
    print(f"  检索命中率 Recall@{TOP_K}: {hit_rate:.0%}")
    print(f"  答案要点准确率: {acc:.0%}")
    print(f"  拒答准确率: {refuse_rate:.0%}")
    print(f"  报告已生成: {report_path}")
    return {"hit_rate": hit_rate, "acc": acc, "refuse_rate": refuse_rate}


if __name__ == "__main__":
    run()
