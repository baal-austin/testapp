import os
from typing import Optional
from pydantic import field_validator, Field, ValidationInfo
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()


class Settings(BaseSettings):
    """
    应用配置类
    使用 pydantic-settings 进行配置验证和类型转换
    """

    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    # ========== 应用基础配置 ==========
    APP_ENV: str = "development"  # 当前运行环境（如 development/production/testing）
    DEBUG: bool = False           # 是否启用调试模式
    APP_SECRET: str = "dev-secret"  # 应用主密钥

    # ========== 数据库配置 ==========
    DATABASE_TYPE: str = "sqlite"  # 数据库类型：sqlite 或 postgresql

    # SQLite 配置
    SQLITE_DATABASE_URL: str = "sqlite:///./word_graph1.db"  # SQLite 数据库文件路径

    # PostgreSQL 配置
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "123456"
    POSTGRES_DATABASE: str = "word_graph"

    # PostgreSQL 连接池配置
    POSTGRES_POOL_SIZE: int = 20
    POSTGRES_MAX_OVERFLOW: int = 10
    POSTGRES_POOL_TIMEOUT: int = 30
    POSTGRES_ECHO: bool = False  # 是否打印SQL语句

    # ========== JWT 配置 ==========
    JWT_SECRET_KEY: str = "dev-jwt-secret"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 43200

    # ========== Redis 配置 ==========
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None

    # ========== 第三方登录配置 ==========
    WECHAT_APPID: str = ""
    WECHAT_SECRET: str = ""
    WECHAT_REDIRECT_URI: str = ""

    QQ_APPID: str = ""
    QQ_SECRET: str = ""
    QQ_REDIRECT_URI: str = ""

    # ========== 邮件服务配置 ==========
    SMTP_SERVER: str = "smtp.qq.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = "770782393@qq.com"
    SMTP_PASSWORD: str = "cqvniouyrgtibeab"
    EMAIL_FROM_NAME: str = "单词图学习系统"

    # ========== 短信服务配置 ==========
    SMS_PROVIDER: str = "aliyun"
    SMS_ACCESS_KEY: str = ""
    SMS_ACCESS_SECRET: str = ""
    SMS_SIGN_NAME: str = "单词图"
    SMS_TEMPLATE_CODE: str = "SMS_123456789"

    # ========== 功能开关配置 ==========
    DISABLE_EMAIL_SENDING: bool = False
    DISABLE_SMS_SENDING: bool = False

    # ========== 动态属性 ==========

    @property
    def DATABASE_URL(self) -> str:
        """根据数据库类型返回完整的数据库连接URL"""
        if self.DATABASE_TYPE == "postgresql":
            return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DATABASE}"
        else:
            return self.SQLITE_DATABASE_URL

    @property
    def DATABASE_ENGINE_CONFIG(self) -> dict:
        """返回数据库引擎配置参数（用于 SQLAlchemy）"""
        if self.DATABASE_TYPE == "postgresql":
            return {
                "pool_size": self.POSTGRES_POOL_SIZE,
                "max_overflow": self.POSTGRES_MAX_OVERFLOW,
                "pool_timeout": self.POSTGRES_POOL_TIMEOUT,
                "pool_pre_ping": True,  # 连接前测试，避免使用断开的连接
                "echo": self.POSTGRES_ECHO,
            }
        else:
            # SQLite 不需要连接池
            return {
                "connect_args": {"check_same_thread": False},  # SQLite 多线程支持
                "echo": self.DEBUG,
            }

    # ========== 验证器 ==========

    @field_validator("JWT_SECRET_KEY")
    @classmethod
    def validate_jwt_secret(cls, v: str, info: ValidationInfo) -> str:
        # 从验证上下文获取 APP_ENV 的值
        app_env = info.data.get("APP_ENV")
        if app_env == "production" and len(v) < 32:
            raise ValueError("生产环境JWT密钥长度必须至少32位")
        return v

    @field_validator("DATABASE_TYPE")
    @classmethod
    def validate_database_type(cls, v: str) -> str:
        if v not in ["sqlite", "postgresql"]:
            raise ValueError("数据库类型必须是 sqlite 或 postgresql")
        return v

    @field_validator("POSTGRES_PORT")
    @classmethod
    def validate_postgres_port(cls, v: int) -> int:
        if v < 1 or v > 65535:
            raise ValueError("PostgreSQL端口必须在1-65535之间")
        return v


# 创建全局配置实例
settings = Settings()

# 测试配置（仅在直接运行此文件时执行）
if __name__ == "__main__":
    print("=" * 50)
    print(f"当前环境: {settings.APP_ENV}")
    print(f"数据库类型: {settings.DATABASE_TYPE}")
    print(f"数据库URL: {settings.DATABASE_URL}")
    print(f"调试模式: {settings.DEBUG}")

    if settings.DATABASE_TYPE == "postgresql":
        print("\nPostgreSQL 连接池配置:")
        print(f"  - 连接池大小: {settings.POSTGRES_POOL_SIZE}")
        print(f"  - 最大溢出: {settings.POSTGRES_MAX_OVERFLOW}")
        print(f"  - 超时时间: {settings.POSTGRES_POOL_TIMEOUT}")
        print(f"  - 打印SQL: {settings.POSTGRES_ECHO}")

    print(f"\nRedis主机: {settings.REDIS_HOST}")
    print("=" * 50)