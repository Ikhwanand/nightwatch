from functools import lru_cache
from typing import Optional
from agno.models.openai import OpenAIChat
from agno.models.nvidia import Nvidia
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict



class Settings(BaseSettings):
    # LLM Settings (OpenAI or Any OpenAI-Compatible Provider)
    model_api_key: str = Field(default="", validation_alias="MODEL_API_KEY")
    model_base_url: Optional[str] = Field(default=None, validation_alias="MODEL_BASE_URL")
    default_model: str = Field(default="gpt-4o", validation_alias="DEFAULT_MODEL")
    fast_model: str = Field(default="gpt-4o-mini", validation_alias="FAST_MODEL")
    openai_compatible: bool = Field(False, description="To setup model provider is Openai or OpenAI-Compatible set to True, else set to False", validation_alias="OPENAI_COMPATIBLE")
    
    # Monitoring Infrastructure
    prometheus_url: str = Field(default="http://localhost:9090")
    loki_url: str = Field(default="http://localhost:3100")
    
    # Database & Storage
    database_url: str = Field(default="postgresql+psycopg://nightwatch:secret@localhost:5532/nightwatch")
    
    # Notifications (Telegram)
    telegram_bot_token: Optional[str] = Field(default=None, validation_alias="TELEGRAM_BOT_TOKEN")
    telegram_chat_id: Optional[str] = Field(default=None, validation_alias="TELEGRAM_CHAT_ID")
    
    # Application Settings
    app_env: str = "development"
    log_level: str = "INFO"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    

@lru_cache
def get_settings() -> Settings:
    return Settings()

def get_model(model_id: Optional[str] = None) -> OpenAIChat | Nvidia:
    """Helper factory to instantiate OpenAIChat or Nvidia model provider.

    Args:
        model_id (Optional[str], optional): Model ID to use. Defaults to settings.default_model.

    Returns:
        OpenAIChat | Nvidia: Configured Agno model instance.
    """
    settings = get_settings()

    # Automatically sanitize base_url: strip trailing '/chat/completions' or slashes if included
    base_url = settings.model_base_url
    if base_url:
        base_url = base_url.removesuffix("/chat/completions").rstrip("/")

    if settings.openai_compatible:
        return OpenAIChat(
            id=model_id or settings.default_model,
            api_key=settings.model_api_key or "not-needed",
            base_url=base_url or None,
        )
    else:
        return Nvidia(
            id=model_id or settings.default_model,
            api_key=settings.model_api_key or "not-needed",
            base_url=base_url or None,
        )