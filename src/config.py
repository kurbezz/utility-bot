from pydantic_settings import BaseSettings


class Config(BaseSettings):
    BOT_TOKEN: str
    BASE_WEBHOOK_URL: str
    WEBHOOK_SECRET: str


config = Config()  # type: ignore
