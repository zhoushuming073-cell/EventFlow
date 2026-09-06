from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置，全部从环境变量读取。"""

    # 运行环境：dev / prod
    env: str = "dev"

    # MySQL
    mysql_host: str = "localhost"
    mysql_port: int = 3306
    mysql_database: str = "eventflow"
    mysql_user: str = "root"
    mysql_password: str = ""

    # WeChat
    wechat_app_id: str = ""
    wechat_app_secret: str = ""

    # JWT
    jwt_secret: str = ""
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24 * 30  # 30 天

    # 是否在本地测试时跳过真实微信调用（仅测试/开发用）
    wechat_mock_openid: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def is_prod(self) -> bool:
        return self.env.lower() in ("prod", "production")

    @property
    def database_url(self) -> str:
        return (
            f"mysql+pymysql://{self.mysql_user}:{self.mysql_password}"
            f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_database}?charset=utf8mb4"
        )

    def validate_production(self) -> None:
        """生产环境启动时的强制校验，缺失关键配置直接抛异常阻止启动。"""
        if not self.is_prod:
            return

        errors: list[str] = []
        if not self.jwt_secret or len(self.jwt_secret) < 16:
            errors.append("JWT_SECRET 缺失或过短（至少 16 字符）")
        if not self.wechat_app_id:
            errors.append("WECHAT_APP_ID 未配置")
        if not self.wechat_app_secret:
            errors.append("WECHAT_APP_SECRET 未配置")
        if self.wechat_mock_openid:
            errors.append("生产环境禁止设置 WECHAT_MOCK_OPENID")

        if errors:
            raise RuntimeError(
                "生产环境配置不完整，拒绝启动：\n  - " + "\n  - ".join(errors)
            )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
