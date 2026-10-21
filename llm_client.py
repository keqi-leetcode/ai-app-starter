"""把大模型调用封装成一个可复用的类。"""

import logging
import time

from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    OpenAI,
    RateLimitError,
)

from config import Settings

logger = logging.getLogger(__name__)


class LLMError(Exception):
    """调用大模型失败。外面（界面层）只需要认这个异常。"""


class LLMRetryableError(LLMError):
    """重试过还是失败：网络超时、限流、服务端 5xx。"""


def _retryable(exc: Exception) -> bool:
    """判断这个异常值不值得重试。"""
    if isinstance(exc, (APITimeoutError, APIConnectionError, RateLimitError)):
        return True
    if isinstance(exc, APIStatusError):
        return exc.status_code >= 500
    return False


class LLMClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._client = OpenAI(
            api_key=settings.llm_api_key.get_secret_value(),
            base_url=settings.llm_base_url,
            max_retries=0,
        )
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.max_attempts = 3

    @property
    def total_tokens(self) -> int:
        return self.prompt_tokens + self.completion_tokens

    def _temperature(self, temperature: float | None) -> float:
        return self.settings.llm_temperature if temperature is None else temperature

    def _create(self, **kwargs):
        """带重试的请求：可重试的错误按 1s / 2s 退避，其它直接抛 LLMError。"""
        for attempt in range(1, self.max_attempts + 1):
            try:
                return self._client.chat.completions.create(**kwargs)
            except Exception as exc:
                if not _retryable(exc):
                    logger.error("不可重试的错误：%s", exc)
                    raise LLMError(str(exc)) from exc
                if attempt == self.max_attempts:
                    logger.error("重试 %d 次仍然失败：%s", self.max_attempts, exc)
                    raise LLMRetryableError(str(exc)) from exc
                wait = 2 ** (attempt - 1)
                logger.warning("第 %d 次失败（%s），%d 秒后重试", attempt, exc, wait)
                time.sleep(wait)

    def chat(
        self,
        messages: list[dict[str, str]],
        temperature: float | None = None,
    ) -> str:
        """非流式调用：返回完整回答，并累计用量。"""
        start = time.perf_counter()
        response = self._create(
            model=self.settings.llm_model,
            messages=messages,
            temperature=self._temperature(temperature),
        )
        elapsed = time.perf_counter() - start

        usage = response.usage
        if usage:
            self.prompt_tokens += usage.prompt_tokens
            self.completion_tokens += usage.completion_tokens

        text = response.choices[0].message.content or ""
        logger.info(
            "chat 完成：%.2fs，本轮 prompt=%s / completion=%s，累计 %d tokens",
            elapsed,
            usage.prompt_tokens if usage else 0,
            usage.completion_tokens if usage else 0,
            self.total_tokens,
        )
        return text

    def stream_chat(
        self,
        messages: list[dict[str, str]],
        temperature: float | None = None,
    ):
        """流式调用：一段一段往外 yield，交给调用方决定怎么显示。"""
        stream = self._create(
            model=self.settings.llm_model,
            messages=messages,
            temperature=self._temperature(temperature),
            stream=True,
            stream_options={"include_usage": True},
        )
        for chunk in stream:
            if chunk.usage:
                self.prompt_tokens += chunk.usage.prompt_tokens
                self.completion_tokens += chunk.usage.completion_tokens
                logger.info("流式结束：累计 %d tokens", self.total_tokens)
                continue
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta
            think = getattr(delta, "reasoning_content", None)
            text = delta.content or ""
            if think:
                yield ("think", think)
            if text:
                yield ("answer", text)