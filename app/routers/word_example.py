from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import List
from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.word_relation import ExampleCreate, ExampleRead, ExampleUpdate
from app.crud.word_relation import (
    get_word_examples, get_example_by_id, create_word_example,
    update_word_example, delete_word_example, get_word_id_by_text, is_exist_example, get_examples_by_word
)

word_example_router = APIRouter(prefix="/words/{word_text}/examples", tags=["word examples"])


# ========== 辅助函数 ==========
def get_word_id_or_404(db: Session, word_text: str) -> int:
    word_id = get_word_id_by_text(db, word_text)
    if not word_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Word not found"
        )
    return word_id


def check_example_word_link(db, example_id, word_id):
    pass


def check_example_word_link_or_404(db: Session, example_id: int, word_id: int):
    if not check_example_word_link(db, example_id, word_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Example not found for this word"
        )

# ========== 基础例句操作 ==========
@word_example_router.get("/", response_model=List[ExampleRead])
def read_word_examples(word_text: str, db: Session = Depends(get_db)):
    """获取单词的所有例句（不含位置和释义信息）"""
    word_id = get_word_id_or_404(db, word_text)
    examples = get_examples_by_word(db, word_id)
    return examples


@word_example_router.get("/{example_id}", response_model=ExampleRead)
def read_word_example_by_id(example_id: int, db: Session = Depends(get_db)):
    """通过例句id获取单词的例句"""
    example = get_example_by_id(db, example_id)
    if not example:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Example not found"
        )
    return example


@word_example_router.post("/", response_model=ExampleRead, status_code=status.HTTP_201_CREATED)
def create_example(
        word_text: str,
        example: ExampleCreate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """为单词创建新例句"""
    # 验证用户权限
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No administrator privileges"
        )

    word_id = get_word_id_by_text(db, word_text)
    if not word_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Word not found"
        )

    db_example = create_word_example(db, word_id, example.dict())
    return db_example


@word_example_router.put("/{example_id}", response_model=ExampleRead)
def update_example(
        word_text: str,
        example_id: int,
        example_update: ExampleUpdate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """更新单词的例句"""
    # 验证用户权限
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No administrator privileges"
        )

    # 验证单词存在
    word_id = get_word_id_by_text(db, word_text)
    if not word_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Word not found"
        )

    # 验证例句存在且属于该单词
    exist_example = is_exist_example(db, example_id, word_id)
    if not exist_example:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Example not found"
        )

    # 更新例句
    update_data = example_update.dict(exclude_unset=True)
    db_example = update_word_example(db, example_id, update_data)
    return db_example


@word_example_router.delete("/{example_id}")
def delete_example(
        word_text: str,
        example_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """安全删除单词的指定例句"""
    # 验证用户权限
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No administrator privileges"
        )

    # 验证单词存在
    word_id = get_word_id_by_text(db, word_text)
    if not word_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Word not found"
        )

    # 验证例句存在且属于该单词
    exist_example = is_exist_example(db, example_id, word_id)
    if not exist_example:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Example not found"
        )

    # 执行删除
    is_delete_example = delete_word_example(db, example_id)
    if is_delete_example:
        return {"message": "Example deleted successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Delete failed"
        )