from sqlalchemy.orm import sessionmaker
from sqlmodel import create_engine, SQLModel, Session
from contextlib import contextmanager
from typing import Generator
from sqlalchemy import event
from sqlalchemy.engine import Engine

# 导入配置类
from app.config import settings


def get_database_engine():
    """
    根据配置创建数据库引擎

    根据不同的环境使用不同的数据库配置
    支持 SQLite、PostgreSQL
    """
    database_url = settings.DATABASE_URL

    if settings.DATABASE_TYPE == "sqlite":
        # SQLite 配置
        engine = create_engine(
            database_url,
            connect_args={"check_same_thread": False},
            echo=settings.DEBUG  # 开发环境显示SQL日志
        )

        # SQLite 特定优化
        @event.listens_for(engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            # 启用外键约束
            cursor.execute("PRAGMA foreign_keys=ON")
            # 启用 WAL 模式，提高并发性能
            cursor.execute("PRAGMA journal_mode=WAL")
            # 设置同步模式为 NORMAL，提高性能（牺牲一点点安全性）
            cursor.execute("PRAGMA synchronous=NORMAL")
            # 设置缓存大小（单位：页）
            cursor.execute("PRAGMA cache_size=-20000")  # 约 20MB 缓存
            cursor.close()


    elif settings.DATABASE_TYPE == "postgresql":

        try:

            # 修改点1: 使用 'postgresql+psycopg://' 作为空URL的前缀

            engine = create_engine(

                "postgresql+psycopg://",  # <--- 这里改成了 +psycopg

                connect_args={

                    "host": settings.POSTGRES_HOST,

                    "port": int(settings.POSTGRES_PORT),

                    "user": settings.POSTGRES_USER,

                    "password": settings.POSTGRES_PASSWORD,

                    "dbname": settings.POSTGRES_DATABASE,  # 注意：参数名从 database 改为 dbname

                    "connect_timeout": 10,

                    "keepalives": 1,

                    "keepalives_idle": 60,

                    "keepalives_interval": 10,

                    "keepalives_count": 5,

                    "application_name": f"word_graph_{settings.APP_ENV}",

                    # psycopg3 默认使用 utf-8，client_encoding 通常不需要显式设置

                },

                pool_pre_ping=True,

                pool_size=settings.POSTGRES_POOL_SIZE,

                max_overflow=settings.POSTGRES_MAX_OVERFLOW,

                pool_timeout=settings.POSTGRES_POOL_TIMEOUT,

                pool_recycle=3600,

                echo=settings.POSTGRES_ECHO or settings.DEBUG,

            )

            print("✅ PostgreSQL (with psycopg3) 引擎创建成功")

        except Exception as e:

            print("❌ 创建 PostgreSQL 引擎失败:")

            print(repr(e))

            raise

        # PostgreSQL 连接后执行的事件
        @event.listens_for(engine, "connect")
        def postgresql_on_connect(dbapi_connection, connection_record):
            """PostgreSQL 连接时的额外设置"""
            cursor = dbapi_connection.cursor()
            try:
                # 设置会话时区为 UTC
                cursor.execute("SET timezone TO 'UTC'")

                # 设置语句超时时间（可选，防止慢查询）
                # cursor.execute("SET statement_timeout = '30s'")

                # 设置锁等待超时（可选）
                # cursor.execute("SET lock_timeout = '10s'")

                # 设置客户端编码
                cursor.execute("SET client_encoding TO 'UTF8'")

                # 设置默认事务隔离级别为 READ COMMITTED
                cursor.execute("SET default_transaction_isolation TO 'read committed'")

            finally:
                cursor.close()

        # 监听连接检出事件（每次从连接池获取连接时触发）
        @event.listens_for(engine, "checkout")
        def receive_checkout(dbapi_connection, connection_record, connection_proxy):
            """连接从连接池取出时的处理"""
            # 可以在这里添加连接验证逻辑
            pass

    else:
        raise ValueError(f"不支持的数据库类型: {settings.DATABASE_TYPE}")

    return engine


# 创建数据库引擎
engine = get_database_engine()

# 创建会话工厂
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False  # 防止提交后对象过期
)


@contextmanager
def get_db_session():
    """
    数据库会话上下文管理器（用于非FastAPI场景）

    使用示例：
    with get_db_session() as session:
        # 使用session进行数据库操作
        user = session.get(User, 1)
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()  # 成功时提交事务
    except Exception as e:
        session.rollback()  # 异常时回滚事务
        raise e
    finally:
        session.close()  # 确保会话关闭


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI 依赖项，提供数据库会话

    在FastAPI路由中使用：
    @app.get("/users/{user_id}")
    def get_user(user_id: int, db: Session = Depends(get_db)):
        user = db.get(User, user_id)
        return user
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()  # 请求成功完成时提交
    except Exception as e:
        db.rollback()  # 发生异常时回滚
        raise e
    finally:
        db.close()  # 请求结束时关闭连接


def create_db_tables():
    """创建所有数据库表"""
    print(f"创建数据库表，环境: {settings.APP_ENV}, 数据库类型: {settings.DATABASE_TYPE}")

    # 根据数据库类型显示不同的信息
    if settings.DATABASE_TYPE == "postgresql":
        print(f"PostgreSQL 连接: {settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DATABASE}")
        print(f"连接池配置: 大小={settings.POSTGRES_POOL_SIZE}, 最大溢出={settings.POSTGRES_MAX_OVERFLOW}")

    SQLModel.metadata.create_all(engine)
    print("✅ 数据库表创建成功!")


def drop_db_tables():
    """删除所有数据库表（仅用于开发和测试）"""
    if settings.APP_ENV == "production":
        raise Exception("❌ 生产环境禁止删除数据库表!")

    print(f"⚠️ 正在删除数据库表: {settings.DATABASE_TYPE}")
    SQLModel.metadata.drop_all(engine)
    print("✅ 数据库表删除成功!")


def verify_database_connection():
    """验证数据库连接是否正常"""
    try:
        with engine.connect() as conn:
            if settings.DATABASE_TYPE == "postgresql":
                result = conn.execute("SELECT version()").scalar()
                print(f"✅ PostgreSQL 连接成功: {result[:50]}...")
            else:
                result = conn.execute("SELECT sqlite_version()").scalar()
                print(f"✅ SQLite 连接成功: 版本 {result}")
            return True
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False


def init_db():
    """初始化数据库（创建表并添加初始数据）"""
    # 验证连接
    if not verify_database_connection():
        print("❌ 数据库连接失败，请检查配置")
        return

    try:
        # 创建数据库表
        create_db_tables()

        # 导入初始数据
        try:
            from .init_data import import_initial_data
            import_initial_data()
            print("✅ 初始数据导入成功!")
        except ImportError:
            print("ℹ️ 未找到初始数据脚本，跳过数据导入")
        except Exception as e:
            print(f"⚠️ 初始数据导入失败: {e}")

        print("🎉 数据库初始化完成!")

    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        raise


# 获取数据库引擎统计信息（仅用于调试）
def get_engine_status():
    """获取数据库引擎状态信息"""
    if settings.DATABASE_TYPE == "postgresql":
        pool = engine.pool
        return {
            "database_type": settings.DATABASE_TYPE,
            "pool_size": pool.size(),
            "checked_in_connections": pool.checkedin(),
            "overflow": pool.overflow(),
            "total_connections": pool.total(),
        }
    return {
        "database_type": settings.DATABASE_TYPE,
        "pool_size": "N/A (SQLite)",
    }


# 开发时自动初始化数据库
if __name__ == "__main__":
    print("=" * 60)
    print(f"数据库初始化工具")
    print("=" * 60)
    print(f"当前环境: {settings.APP_ENV}")
    print(f"数据库类型: {settings.DATABASE_TYPE}")
    print(f"数据库URL: {settings.DATABASE_URL}")
    print("-" * 60)

    init_db()

    if settings.DATABASE_TYPE == "postgresql":
        print("-" * 60)
        print("连接池状态:")
        status = get_engine_status()
        for key, value in status.items():
            print(f"  {key}: {value}")

    print("=" * 60)