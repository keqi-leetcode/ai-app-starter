"""用 LLMClient 重写的聊天程序：配置、重试、日志、用量全交给类，脚本只管界面。"""

import logging

from config import Settings
from llm_client import LLMClient, LLMError

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

settings = Settings()
client = LLMClient(settings)

messages: list[dict[str, str]] = [
    {"role": "system", "content": settings.llm_system},
]

while True:
    try:
        question = input("\n你：").strip()
    except (EOFError, KeyboardInterrupt):
        print("\n拜拜～")
        break

    if question in ("exit", "quit", "退出"):
        print("拜拜～")
        break
    if not question:
        continue

    messages.append({"role": "user", "content": question})

    parts: list[str] = []
    try:
        for kind, piece in client.stream_chat(messages):
            if kind == "think":
                continue
            print(piece, end="", flush=True)
            parts.append(piece)
    except LLMError as exc:
        print(f"\n[失败] {exc}")
        messages.pop()
        continue

    print()
    answer = "".join(parts)
    if answer:
        messages.append({"role": "assistant", "content": answer})