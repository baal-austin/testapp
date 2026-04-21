# crud/word_relation.py
from sqlmodel import select, Session
from typing import List, Optional

from app.models.word import Word
from sqlalchemy import func

from app.schemas.word import WordCreate, WordUpdate


def create_word(db: Session, word: WordCreate) -> Word:
    """创建新单词"""
    db_word = Word.model_validate(word)
    db.add(db_word)
    db.commit()
    db.refresh(db_word)
    return db_word


def get_word(db: Session, word_id: int) -> Optional[Word]:
    """根据ID获取单词"""
    return db.get(Word, word_id)


def get_word_by_normalized(db: Session, normalized_word: str) -> Optional[Word]:
    """根据标准化单词获取单词"""
    statement = select(Word).where(Word.normalized_word == normalized_word)
    return db.exec(statement).first()


def get_words(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        is_common: Optional[bool] = None,
        difficulty_level_id: Optional[int] = None
) -> List[Word]:
    """获取单词列表，支持过滤"""
    statement = select(Word)

    if is_common is not None:
        statement = statement.where(Word.is_common == is_common)

    if difficulty_level_id is not None:
        statement = statement.where(Word.difficulty_level_id == difficulty_level_id)

    statement = statement.offset(skip).limit(limit)
    result = db.exec(statement).all()
    return list(result)  # 转换为列表


def update_word(db: Session, word_id: int, word_update: WordUpdate) -> Optional[Word]:
    """更新单词"""
    db_word = db.get(Word, word_id)
    if not db_word:
        return None

    # 只更新提供的字段
    update_data = word_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_word, field, value)

    db.add(db_word)
    db.commit()
    db.refresh(db_word)
    return db_word


def delete_word(db: Session, word_id: int) -> bool:
    """删除单词"""
    db_word = db.get(Word, word_id)
    if not db_word:
        return False

    db.delete(db_word)
    db.commit()
    return True


def search_words(db: Session, query: str, limit: int = 20) -> List[Word]:
    """搜索单词"""
    query_lower = query.lower()
    statement = select(Word).where(
        func.lower(Word.word).like(f"%{query_lower}%") |
        func.lower(Word.normalized_word).like(f"%{query_lower}%")
    ).limit(limit)
    result = db.exec(statement).all()
    return list(result)  # 转换为列表
