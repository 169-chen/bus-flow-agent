"""公交客流智能问答助手 - 交互式演示入口。

运行：python app.py
可选：配置 .env 中的 LLM_API_KEY 后可使用真实大模型生成。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from src.pipeline import RAGPipeline


def main():
    print("=" * 60)
    print("  公交客流智能问答助手  |  输入 q 退出")
    print("=" * 60)
    pipe = RAGPipeline()
    print(f"已加载 {len(pipe.docs)} 篇文档，切分为 {len(pipe.chunks)} 个文本块\n")
    print("可以试试：'公交IC卡数据包含哪些核心字段？'")
    print("         '数据清洗包含哪些规则？'\n")

    while True:
        q = input("问：").strip()
        if q.lower() in ("q", "quit", "exit"):
            print("再见")
            break
        if not q:
            continue
        result = pipe.ask(q)
        print(f"\n答（{result['mode']}）：")
        print(result["answer"])
        print(f"\n召回来源：{[c['doc_id'] for c in result['contexts']]}")
        print("-" * 60)


if __name__ == "__main__":
    main()
