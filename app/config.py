from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    TELEGRAM_TOKEN: str
    BASE_URL: str
    WEBHOOK_SECRET: str

    SYNC_CLIENT_ID: str
    SYNC_CLIENT_SECRET: str
    SYNC_BASE_URL: str

    VIP_CHAT_ID: int
    ADMIN_IDS: str
    SUPPORT_USERNAME: str = "suporte"

    @property
    def admin_id_set(self) -> set[int]:
        return {int(x.strip()) for x in self.ADMIN_IDS.split(",") if x.strip()}

    @property
    def webhook_path(self) -> str:
        return f"/tg/webhook/{self.WEBHOOK_SECRET}"

    @property
    def webhook_url(self) -> str:
        return self.BASE_URL.rstrip("/") + self.webhook_path

settings = Settings()
  
