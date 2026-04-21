
# app/router/word.py
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session
from typing import List

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.word import WordCreate, WordRead, WordUpdate, WordSimple
from app.crud.word import (
    create_word, get_word, get_word_by_word, get_words,
    update_word, delete_word, search_words, increment_view_count,
    update_user_feedback, get_word_id_by_text
)

words_router = APIRouter(prefix="/words", tags=["words"])


@words_router.get("/id", response_model=dict)
def get_word_id_by_text_route(
        word_text: str = Query(..., description="单词文本"),
        db: Session = Depends(get_db)
):
    """通过单词文本获取单词ID"""
    word_id = get_word_id_by_text(db, word_text)
    if not word_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Word not found"
        )

    return {"word_text": word_text, "word_id": word_id}


@words_router.post("/", response_model=WordRead, status_code=status.HTTP_201_CREATED)
def create_new_word(
        word: WordCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """创建新单词"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create words"
        )

    db_word = create_word(db, word)
    if not db_word:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Word already exists"
        )
    return db_word


@words_router.get("/", response_model=List[WordSimple])
def read_words(
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db)
):
    """获取单词列表（分页）"""
    words = get_words(db, skip=skip, limit=limit)
    return words


@words_router.get("/{word_id}", response_model=WordRead)
def read_word(word_id: int, db: Session = Depends(get_db)):
    """根据ID获取单词详情"""
    word = get_word(db, word_id)
    if not word:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Word not found"
        )

    # 增加浏览计数
    increment_view_count(db, word_id)
    return word


@words_router.get("/by-word/{word_text}", response_model=WordRead)
def read_word_by_text(word_text: str, db: Session = Depends(get_db)):
    """通过单词文本获取单词详情"""
    word = get_word_by_word(db, word_text)
    if not word:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Word not found"
        )

    # 增加浏览计数
    increment_view_count(db, word.id)
    return word


@words_router.put("/{word_id}", response_model=WordRead)
def update_existing_word(
        word_id: int,
        word_update: WordUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """通过ID更新单词"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update words"
        )

    word = update_word(db, word_id, word_update)
    if not word:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Word not found"
        )
    return word


@words_router.put("/by-word/{word_text}", response_model=WordRead)
def update_word_by_text(
        word_text: str,
        word_update: WordUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """通过单词文本更新单词"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update words"
        )

    # 先找到单词
    word = get_word_by_word(db, word_text)
    if not word:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Word not found"
        )

    # 更新单词
    return update_word(db, word.id, word_update)


@words_router.delete("/{word_id}")
def delete_existing_word(
        word_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """通过ID删除单词"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete words"
        )

    success = delete_word(db, word_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Word not found"
        )
    return {"message": "Word deleted successfully"}


@words_router.delete("/by-word/{word_text}")
def delete_word_by_text(
        word_text: str,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """通过单词文本删除单词"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete words"
        )

    # 先找到单词
    word = get_word_by_word(db, word_text)
    if not word:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Word not found"
        )

    # 删除单词
    success = delete_word(db, word.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Word not found"
        )
    return {"message": "Word deleted successfully"}


@words_router.get("/search/", response_model=List[WordSimple])
def search_words_endpoint(
        query: str = Query(..., min_length=1, max_length=50),
        limit: int = Query(20, ge=1, le=100),
        db: Session = Depends(get_db)
):
    """搜索单词（用于预提示）"""
    words = search_words(db, query, limit)
    return words


@words_router.post("/{word_id}/feedback/{feedback_type}")
def submit_word_feedback(
        word_id: int,
        feedback_type: str,
        db: Session = Depends(get_db)
):
    """提交单词反馈（认识、不认识、不确定）"""
    valid_feedback_types = ["known", "unknown", "uncertain"]
    if feedback_type not in valid_feedback_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Feedback type must be one of: {', '.join(valid_feedback_types)}"
        )

    word = update_user_feedback(db, word_id, feedback_type)
    if not word:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Word not found"
        )

    return {"message": f"Feedback recorded: {feedback_type}"}
