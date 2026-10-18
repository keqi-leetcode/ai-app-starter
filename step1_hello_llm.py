"""
第一步：调通大模型 API。

这个脚本做三件事：
  1. 从 .env 读取你的 Key 和配置
  2. 把一条消息发给大模型
  3. 打印它的回复和 token 用量

运行：python step1_hello_llm.py
"""

import os
import sys

from dotenv import load_dotenv
from openai import OpenAI


def main() -> None:
    # 读取 .env 文件里的配置
    load_dotenv()

    api_key = os.getenv("LLM_API_KEY")
    base_url = os.getenv("LLM_BASE_URL")
    model = os.getenv("LLM_MODEL")

    # 提前检查，给出人话的错误提示，而不是一堆英文堆栈
    if not api_key or api_key.startswith("在这里填"):
        sys.exit("❌ 还没填 API Key，请打开 .env 文件填入 LLM_API_KEY")
    if not base_url or not model:
        sys.exit("❌ .env 里的 LLM_BASE_URL 或 LLM_MODEL 没填")

    # 创建客户端。所有主流平台的接口都兼容这一套，所以换平台只改 .env 就行
    client = OpenAI(api_key=api_key, base_url=base_url)

    print(f"📡 正在调用模型：{model}\n")

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                # system：设定模型的角色和行为，是 Prompt 工程最常用的旋钮
                {
                    "role": "system",
                    "content": "你是一个简洁的编程助教，回答控制在三句话以内。",
                },
                # user：用户的问题
                {"role": "user", "content": "用一句话解释什么是 RAG？"},
            ],
            # temperature 越高越随机、越低越稳定。0 适合要准确答案的场景
            temperature=0.3,
        )
    except Exception as exc:  # noqa: BLE001
        sys.exit(f"❌ 调用失败：{exc}\n\n检查一下 Key、base_url、模型名是否正确，以及网络是否通。")

    answer = response.choices[0].message.content
    print("=" * 60)
    print(answer)
    print("=" * 60)

    # token 用量：这是后面做成本统计和模型路由的基础，JD 里明确提到过
    usage = response.usage
    print(f"\n📊 token 用量：")
    print(f"   输入 prompt_tokens     : {usage.prompt_tokens}")
    print(f"   输出 completion_tokens : {usage.completion_tokens}")
    print(f"   合计 total_tokens      : {usage.total_tokens}")


if __name__ == "__main__":
    main()
