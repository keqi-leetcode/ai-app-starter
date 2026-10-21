"""
Day 3 第一步：把"问一次"改成"一直问"。
运行：python step3_chat.py
"""
import os
import sys
import argparse
import logging

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("app.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)

api_key = os.getenv("LLM_API_KEY")
base_url = os.getenv("LLM_BASE_URL")
model = os.getenv("LLM_MODEL")

parser = argparse.ArgumentParser(description="我的第一个大模型聊天脚本")
parser.add_argument("--model", help="模型名，不填就用 .env 里的")
parser.add_argument("--system", help="让模型扮演什么角色")
parser.add_argument("--temperature", type=float, help="温度 0~2，越高越随机")
args = parser.parse_args()

model = args.model or model
TEMPERATURE = 0.5 if args.temperature is None else args.temperature



if not api_key or api_key.startswith("在这里填"):
    sys.exit("❌ 还没填 API Key")
if not base_url or not model:
    sys.exit("❌ .env 里的 LLM_BASE_URL 或 LLM_MODEL 没填")

client = OpenAI(api_key=api_key, base_url=base_url)
logger.info("启动：model=%s, temperature=%s", model, TEMPERATURE)

SYSTEM_PROMPT = args.system or "你是一个讲技术很清楚的人。"


# ① 历史就放在循环外面 —— 它必须在每一轮之间活下来
messages= [
    {"role": "system", "content": SYSTEM_PROMPT},
]

while True:
    question = input("\n你：").strip()
    logger.info("收到问题（%d 字）", len(question))

    if question in ("exit", "quit", "退出"):
        print("拜拜～")
        break
    if not question:
        continue
    messages.append (
    {"role": "user", "content": question}
    )
    # ② TODO：把 question 追加进 messages（你自己写）
    #    提示：列表用 .append(...)，字典的形状照抄上面初始化那行，role 是 "user"
    try:
        stream = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=TEMPERATURE,
            stream=True,
        )
    except Exception as exc:
        logger.error("调用失败：%s", exc)
        messages.pop()
        continue
    phase = ""
    answer_parts = []

    for chunk in stream:
        if not chunk.choices:
            continue
        delta = chunk.choices[0].delta
        think = getattr(delta, "reasoning_content", None)   # 思考片段
        text = delta.content or ""                          # 回答片段

        if think:
            if phase != "think":
                print("\n[思考] ", end="", flush=True)
                phase = "think"
            print(think, end="", flush=True)

        if text:
            if phase != "answer":
                print("\n[回答] ", end="", flush=True)
                phase = "answer"
            print(text, end="", flush=True)
            answer_parts.append(text)

    print()
    answer = "".join(answer_parts)
    logger.info("回答完成（%d 字）", len(answer))
    if answer:
        messages.append({"role": "assistant", "content": answer})
    # ③ TODO：把 answer 也追加进 messages（你自己写）
    #    提示：形状一样，role 换成 "assistant"