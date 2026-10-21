from config import Settings

settings = Settings()
print("模型：", settings.llm_model)
print("温度：", settings.llm_temperature)
print("Key（打码）：", settings.llm_api_key)
print("Key 长度：", len(settings.llm_api_key.get_secret_value()))