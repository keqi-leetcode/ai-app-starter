import logging

from config import Settings
from llm_client import LLMClient, LLMError

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

client = LLMClient(Settings())
try:
    answer = client.chat([{"role": "user", "content": "用一句话解释什么是 token"}])
except LLMError as exc:
    print("调用失败了：", exc)
else:
    print("\n回答：", answer)
    print("累计 tokens：", client.total_tokens)

    print("\n—— 流式 ——")
parts = []
for kind, piece in client.stream_chat(
    [{"role": "user", "content": "用三句话解释 RAG 是什么"}]
):
    if kind == "think":
        continue
    print(piece, end="", flush=True)
    parts.append(piece)

print("\n回答长度：", len("".join(parts)))
print("累计 tokens：", client.total_tokens)