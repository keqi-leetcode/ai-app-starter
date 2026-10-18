"""
第二步：流式输出（streaming）。

区别只有一个：把 stream=True 打开。
普通模式要等模型全部想完才一次性返回；流式模式会一个字一个字地冒出来。
所有 AI 聊天产品"打字机效果"的底层就是这个。

运行：python step2_stream.py
"""

import os
import sys
import time

from dotenv import load_dotenv
from openai import OpenAI


def main() -> None:
    load_dotenv()

    api_key = os.getenv("LLM_API_KEY")
    base_url = os.getenv("LLM_BASE_URL")
    model = os.getenv("LLM_MODEL")

    if not api_key or api_key.startswith("在这里填"):
        sys.exit("❌ 还没填 API Key，请打开 .env 文件填入 LLM_API_KEY")
    if not base_url or not model:
        sys.exit("❌ .env 里的 LLM_BASE_URL 或 LLM_MODEL 没填")

    client = OpenAI(api_key=api_key, base_url=base_url)

    question = "给我讲讲 RAG 里的文档切分（chunking）为什么重要，200 字左右。"
    print(f"❓ {question}\n")
    print("=" * 60)

    start = time.time()

    try:
        stream = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "你是一个讲技术很清楚的人。"},
                {"role": "user", "content": question},
            ],
            temperature=1.5,
            stream=True,  # ← 唯一的区别
        )

        # 一段一段地接收，每收到一段就立刻打印
        char_count = 0
        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                print(delta, end="", flush=True)
                char_count += len(delta)
            else:
                # 有时会收到没有正文的空包，跳过即可
                pass

    except Exception as exc:  # noqa: BLE001
        sys.exit(f"\n❌ 调用失败：{exc}")

    elapsed = time.time() - start
    print("\n" + "=" * 60)
    print(f"\n⏱️  首字到最后一个字共用时 {elapsed:.1f} 秒，共输出约 {char_count} 个字符")
    print("💡 注意：流式模式下很多平台默认不返回 token 用量，")
    print("   需要额外加 stream_options={'include_usage': True} 才会带上。")
    print("   这个坑你先记住，后面做接口时用得上。")


if __name__ == "__main__":
    main()
