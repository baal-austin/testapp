import os
import random
import string
import uuid
from datetime import datetime, timedelta
from typing import Optional

import bcrypt
from fastapi import HTTPException
import jwt
from jwt import PyJWTError as JWTError
from passlib.context import CryptContext
import redis
import logging

logger = logging.getLogger(__name__)
# ========== 密码哈希配置 ==========
# 使用bcrypt算法进行密码哈希，这是目前最安全的密码哈希方式之一
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ========== JWT令牌配置 ==========
# 注意：在生产环境中，SECRET_KEY必须设置为强随机字符串，且妥善保管
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-key-change-in-production")
ALGORITHM = "HS256"  # 使用HMAC-SHA256算法签名
ACCESS_TOKEN_EXPIRE_MINUTES = 30 * 24 * 60  # 令牌有效期：30天
# 安全配置
SECURE_ALGORITHMS = ["HS256", "RS256", "ES256"]
MIN_SECRET_KEY_LENGTH = 32
JWT_SECRET_KEYS = [
    os.getenv("JWT_SECRET_KEY_CURRENT"),
    os.getenv("JWT_SECRET_KEY_PREVIOUS")  # 用于平滑过渡
]
# ========== Redis配置（用于验证码存储） ==========
# Redis用于存储临时验证码，相比数据库更适合这种高频读写场景
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=int(os.getenv("REDIS_DB", 0)),
    decode_responses=True,  # 自动解码返回字符串
    socket_connect_timeout=5,  # 连接超时
    retry_on_timeout=True,     # 超时重试
    max_connections=10,         # 连接池大小
    health_check_interval=30  # 健康检查
)




def validate_jwt_config():
    """验证JWT配置安全性"""
    # 验证算法安全性
    if ALGORITHM not in SECURE_ALGORITHMS:
        raise ValueError(f"不安全的JWT算法: {ALGORITHM}")

    if ALGORITHM == "none":
        raise ValueError("JWT 'none' 算法被明确禁止")

    # 验证密钥强度
    if len(SECRET_KEY) < MIN_SECRET_KEY_LENGTH:
        raise ValueError(f"密钥太短，至少需要 {MIN_SECRET_KEY_LENGTH} 字符")

    print("✅ JWT配置安全检查通过")
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证明文密码与哈希密码是否匹配"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def get_password_hash(password: str):
    """生成密码的bcrypt哈希值"""
    # 生成盐并哈希密码（bcrypt自动处理加盐）
    # rounds参数是成本因子，默认是12，可以根据需要调整
    hashed_bytes = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=12))
    # 将得到的字节串（如 b'$2b$12$...'）转为字符串存入数据库
    hashed_password = hashed_bytes.decode('utf-8')
    return hashed_password


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    创建安全的JWT访问令牌

    Args:
        data: 要编码到令牌中的数据
        expires_delta: 可选的自定义过期时间

    Returns:
        str: 编码后的JWT令牌

    Raises:
        HTTPException: 如果安全配置检查失败
    """
    try:
        # 验证配置安全性
        validate_jwt_config()

        # 复制数据避免修改原字典
        to_encode = data.copy()

        # 设置令牌过期时间
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

        # 添加标准JWT声明
        to_encode.update({
            "exp": expire,  # 过期时间
            "iat": datetime.utcnow(),  # 签发时间
            "jti": str(uuid.uuid4()),  # 唯一标识
            "iss": "word-management-api",  # 签发者
            "aud": "word-app-users",  # 受众
        })

        # 使用JWT编码数据
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

        # 可选：将jti存入Redis，用于令牌吊销
        if redis_client:
            token_id = to_encode["jti"]
            expire_timestamp = int(expire.timestamp())
            redis_client.setex(f"token:{token_id}", expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
                               "valid")

        return encoded_jwt

    except ValueError as e:
        raise HTTPException(status_code=500, detail=f"安全配置错误: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"令牌创建失败: {str(e)}")


def verify_token(token: str) -> Optional[dict]:
    """
    验证并解码JWT令牌

    Args:
        token: JWT令牌字符串

    Returns:
        Optional[dict]: 解码后的数据，如果令牌无效返回None
    """
    try:
        # 解码令牌，自动验证签名和过期时间
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        # 令牌无效（签名错误、过期、格式错误等）
        return None


def generate_verification_code(length: int = 6) -> str:
    """生成指定长度的数字验证码"""
    return ''.join(random.choices(string.digits, k=length))


VERIFY_CODE_PREFIX = "verify_code"
ATTEMPT_COUNT_PREFIX = "verify_code_attempts"
DEFAULT_CODE_EXPIRE = 300  # 5分钟
DEFAULT_ATTEMPT_EXPIRE = 3600  # 1小时
MAX_ATTEMPTS = 3


def store_verification_code(
        identifier: str,
        code: str,
        purpose: str,
        expires_in: int = DEFAULT_CODE_EXPIRE,
) -> bool:
    """
    存储验证码到Redis（安全增强版）

    Args:
        identifier: 用户标识（邮箱/手机号）
        code: 验证码
        purpose: 用途（register/login/reset_password）
        expires_in: 过期时间（秒），默认5分钟

    Returns:
        bool: 存储是否成功
    """
    if not all([identifier, code, purpose]):
        logger.error("参数缺失: identifier=%s, purpose=%s", identifier, purpose)
        return False

    key = f"{VERIFY_CODE_PREFIX}:{purpose}:{identifier}"
    try:
        # 存储验证码（可加盐增强安全性）
        redis_client.setex(key, expires_in, code)
        logger.info(
            "验证码存储成功",
            extra={
                "key": key,
                "expires_in": expires_in,
                "identifier": identifier[:3] + "****",  # 脱敏
            },
        )
        return True
    except Exception as e:
        logger.error(
            "验证码存储失败",
            exc_info=True,
            extra={"identifier": identifier, "purpose": purpose},
        )
        return False


def verify_code(
        identifier: str,
        code: str,
        purpose: str,
        max_attempts: int = MAX_ATTEMPTS,
        attempt_expire: int = DEFAULT_ATTEMPT_EXPIRE,
) -> bool:
    """
    验证验证码是否正确（安全增强版）

    Args:
        identifier: 用户标识（邮箱/手机号）
        code: 用户输入的验证码
        purpose: 验证码用途（如register/login）
        max_attempts: 最大尝试次数（防暴力破解）
        attempt_expire: 尝试次数记录过期时间（秒）

    Returns:
        bool: 验证码是否正确
    """
    if not all([identifier, code, purpose]):
        logger.error("参数缺失: identifier=%s, purpose=%s", identifier, purpose)
        return False

    attempt_key = f"{ATTEMPT_COUNT_PREFIX}:{purpose}:{identifier}"
    code_key = f"{VERIFY_CODE_PREFIX}:{purpose}:{identifier}"

    try:
        # 检查尝试次数
        attempts = int(redis_client.get(attempt_key) or 0)
        if attempts >= max_attempts:
            logger.warning("验证码尝试次数超限: %s", attempt_key)
            return False

        # 获取并比对验证码
        stored_code = redis_client.get(code_key)
        if stored_code and stored_code.strip() == code.strip():
            # 验证成功，清理数据
            redis_client.delete(code_key)
            redis_client.delete(attempt_key)
            logger.info(
                "验证码验证成功",
                extra={"key": code_key, "identifier": identifier[:3] + "****"},
            )
            return True
        else:
            # 验证失败，记录尝试次数
            redis_client.incr(attempt_key)
            redis_client.expire(attempt_key, attempt_expire)
            logger.warning(
                "验证码不匹配",
                extra={
                    "stored_code": stored_code,
                    "input_code": code,
                    "attempts": attempts + 1,
                },
            )
            return False
    except Exception as e:
        logger.error(
            "验证码验证异常",
            exc_info=True,
            extra={"identifier": identifier, "purpose": purpose},
        )
        return False


def generate_username() -> str:
    """为第三方登录用户生成唯一用户名"""
    prefix = "user"
    # 生成8位随机数字作为后缀
    random_suffix = ''.join(random.choices(string.digits, k=8))
    return f"{prefix}_{random_suffix}"


def test_verify_code_with_bytes():
    store_verification_code("test_key", "123456", "register")
    assert verify_code("test_key", "123456", "register") is True


if __name__ == "__main__":
    test_verify_code_with_bytes()
