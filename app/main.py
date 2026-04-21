# main.py
from typing import AsyncContextManager

from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.routers.auth import auths_router
from app.routers.note import notes_router
from app.routers.relation import relations_router
from app.routers.relation_book import relation_books_router

from app.routers.user import users_router
from app.routers.word import words_router
from app.routers.word_definition import word_definition_router
from app.routers.word_example import word_example_router
from app.routers.word_form import word_form_router
from app.routers.word_pronunciation import word_pronunciation_router
from app.routers.word_tag import word_tag_router
from app.routers.wordbook import wordbooks_router
from app.routers.study import study_router
from database import create_db_tables


# 导入所有API端点
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncContextManager[None]:
    # Startup: 应用启动前执行
    print("启动应用...")
    try:
        create_db_tables()  # 初始化数据库
        yield
    finally:
        # Shutdown: 应用关闭后执行
        print("关闭应用，清理资源...")
        # 可以添加数据库连接池关闭、缓存清理等代码

app = FastAPI(
    title="单词管理系统",
    description="一个用于管理单词及其关系的API",
    version="1.0.0",
    lifespan=lifespan,
)

# 包含所有路由
app.include_router(users_router)
app.include_router(auths_router)
app.include_router(words_router)
app.include_router(word_definition_router)
app.include_router(word_example_router)
app.include_router(word_form_router)
app.include_router(word_pronunciation_router)
app.include_router(word_tag_router)
app.include_router(notes_router)
app.include_router(relations_router)
app.include_router(wordbooks_router)
app.include_router(relation_books_router)
app.include_router(study_router)
@app.get("/")
def read_root():
    return {"message": "欢迎使用单词管理系统API"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
