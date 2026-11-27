"""项目配置：路径、检索参数、大模型接口（可选）。"""
from pathlib import Path
import os

ROOT = Path(__file__).resolve().parent.parent
KB_DIR = ROOT / "data" / "knowledge"
TESTSET_PATH = ROOT / "evaluation" / "testset.json"
REPORT_DIR = ROOT / "evaluation" / "reports"

# 检索与切分参数
CHUNK_SIZE = 220        # 单个分块的最大字符数
CHUNK_OVERLAP = 40      # 长段落硬切分时的重叠字符数
TOP_K = 3               # 默认召回的文档块数量

# 大模型配置（可选）：不填则使用内置的抽取式生成，项目依然可运行
LLM_API_KEY = os.environ.get("LLM_API_KEY", "").strip()
LLM_BASE_URL = os.environ.get(
    "LLM_BASE_URL", "https://api.deepseek.com/v1"
).rstrip("/")
LLM_MODEL = os.environ.get("LLM_MODEL", "deepseek-chat")
