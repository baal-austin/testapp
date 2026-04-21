# app/crud/word_relations.py
from sqlmodel import Session, select, delete
from typing import List, Optional

from app.models.enums import TagType
from app.models.word import Word, WordDefinition, Example, WordForm, WordPronunciation, Tag, WordTagLink, ExampleWord


def get_word_id_by_text(db: Session, word_text: str) -> Optional[int]:
    """通过单词文本获取单词ID"""
    normalized = word_text.lower()
    statement = select(Word).where(
        (Word.word == word_text) |
        (Word.normalized_word == normalized)
    )
    word = db.execute(statement).scalars().first()
    return word.id if word else None


# WordDefinition 相关操作
def get_word_definitions(db: Session, word_id: int) -> List[WordDefinition]:
    """获取单词的所有定义"""
    statement = select(WordDefinition).where(WordDefinition.word_id == word_id)
    return db.execute(statement).scalars().all()


def is_exist_definition(db, definition_id, word_id):
    return db.query(WordDefinition).filter(
        WordDefinition.id == definition_id,
        WordDefinition.word_id == word_id
    ).first()


def get_definition_by_id(db: Session, definition_id: int) -> Optional[WordDefinition]:
    """通过ID获取定义"""
    return db.get(WordDefinition, definition_id)


def create_word_definition(db: Session, word_id: int, definition_data: dict) -> Optional[WordDefinition]:
    """为单词创建新定义"""
    db_definition = WordDefinition(**definition_data, word_id=word_id)
    db.add(db_definition)
    db.commit()
    db.refresh(db_definition)
    return db_definition


def update_word_definition(db: Session, definition_id: int, definition_data: dict) -> Optional[WordDefinition]:
    """更新定义"""
    db_definition = db.get(WordDefinition, definition_id)
    for field, value in definition_data.items():
        setattr(db_definition, field, value)

    db.add(db_definition)
    db.commit()
    db.refresh(db_definition)
    return db_definition


def delete_word_definition(db: Session, definition_id: int) -> bool:
    """删除定义"""
    db_definition = db.get(WordDefinition, definition_id)
    if not db_definition:
        return False

    db.delete(db_definition)
    db.commit()
    return True


# Example 相关操作
def get_word_examples(db: Session, word_id: int) -> List[Example]:
    """获取单词的所有例句"""
    statement = select(Example).where(Example.word_id == word_id)
    return db.execute(statement).scalars().all()


def is_exist_example(db, example_id, word_id):
    """检查例句是否存在且属于该单词"""
    return db.query(Example).filter(
        Example.id == example_id,
        Example.word_id == word_id
    ).first()


def get_example_by_id(db: Session, example_id: int) -> Optional[Example]:
    """通过ID获取例句"""
    return db.get(Example, example_id)


def create_word_example(db: Session, word_id: int, example_data: dict) -> Optional[Example]:
    """为单词创建新例句"""
    db_example = Example(**example_data, word_id=word_id)
    db.add(db_example)
    db.commit()
    db.refresh(db_example)
    return db_example


def update_word_example(db: Session, example_id: int, example_data: dict) -> Optional[Example]:
    """更新例句"""
    db_example = db.get(Example, example_id)
    if not db_example:
        return None

    for field, value in example_data.items():
        setattr(db_example, field, value)

    db.add(db_example)
    db.commit()
    db.refresh(db_example)
    return db_example


def delete_word_example(db: Session, example_id: int) -> bool:
    """删除例句"""
    db_example = db.get(Example, example_id)
    if not db_example:
        return False

    db.delete(db_example)
    db.commit()
    return True


# WordForm 相关操作
def get_word_forms(db: Session, word_id: int) -> List[WordForm]:
    """获取单词的所有形式"""
    statement = select(WordForm).where(WordForm.word_id == word_id)
    return db.execute(statement).scalars().all()


def is_exist_form(db, form_id, word_id):
    """检查词形是否存在且属于该单词"""
    return db.query(WordForm).filter(
        WordForm.id == form_id,
        WordForm.word_id == word_id
    ).first()


def get_form_by_id(db: Session, form_id: int) -> Optional[WordForm]:
    """通过ID获取形式"""
    return db.get(WordForm, form_id)


def create_word_form(db: Session, word_id: int, form_data: dict) -> Optional[WordForm]:
    """为单词创建新形式"""
    db_form = WordForm(**form_data, word_id=word_id)
    db.add(db_form)
    db.commit()
    db.refresh(db_form)
    return db_form


def update_word_form(db: Session, form_id: int, form_data: dict) -> Optional[WordForm]:
    """更新形式"""
    db_form = db.get(WordForm, form_id)
    if not db_form:
        return None

    for field, value in form_data.items():
        setattr(db_form, field, value)

    db.add(db_form)
    db.commit()
    db.refresh(db_form)
    return db_form


def delete_word_form(db: Session, form_id: int) -> bool:
    """删除形式"""
    db_form = db.get(WordForm, form_id)
    if not db_form:
        return False

    db.delete(db_form)
    db.commit()
    return True


# WordPronunciation 相关操作
def get_word_pronunciations(db: Session, word_id: int) -> List[WordPronunciation]:
    """获取单词的所有发音"""
    statement = select(WordPronunciation).where(WordPronunciation.word_id == word_id)
    return db.execute(statement).scalars().all()


def is_exist_pronunciation(db, pronunciation_id, word_id):
    """检查发音是否存在且属于该单词"""
    return db.query(WordPronunciation).filter(
        WordPronunciation.id == pronunciation_id,
        WordPronunciation.word_id == word_id
    ).first()


def get_pronunciation_by_id(db: Session, pronunciation_id: int) -> Optional[WordPronunciation]:
    """通过ID获取发音"""
    return db.get(WordPronunciation, pronunciation_id)


def create_word_pronunciation(db: Session, word_id: int, pronunciation_data: dict) -> Optional[WordPronunciation]:
    """为单词创建新发音"""
    db_pronunciation = WordPronunciation(**pronunciation_data, word_id=word_id)
    db.add(db_pronunciation)
    db.commit()
    db.refresh(db_pronunciation)
    return db_pronunciation


def update_word_pronunciation(db: Session, pronunciation_id: int, pronunciation_data: dict) \
        -> Optional[WordPronunciation]:
    """更新发音"""
    db_pronunciation = db.get(WordPronunciation, pronunciation_id)
    if not db_pronunciation:
        return None

    for field, value in pronunciation_data.items():
        setattr(db_pronunciation, field, value)

    db.add(db_pronunciation)
    db.commit()
    db.refresh(db_pronunciation)
    return db_pronunciation


def delete_word_pronunciation(db: Session, pronunciation_id: int) -> bool:
    """删除发音"""
    db_pronunciation = db.get(WordPronunciation, pronunciation_id)
    if not db_pronunciation:
        return False

    db.delete(db_pronunciation)
    db.commit()
    return True


# Tag 相关操作
def get_word_tags(db: Session, word_id: int) -> List[Tag]:
    """获取单词的所有标签"""
    statement = select(Tag).join(WordTagLink).where(WordTagLink.word_id == word_id)
    return db.execute(statement).scalars().all()


def is_exist_tag_relation(db, word_id: int, tag_name: str) -> bool:
    """检查标签关联是否存在"""
    statement = select(WordTagLink).join(Tag).where(
        WordTagLink.word_id == word_id,
        Tag.name == tag_name
    )
    return db.execute(statement).scalars().first() is not None


def get_tag_by_name(db: Session, tag_name: str) -> Optional[Tag]:
    """通过名称获取标签"""
    statement = select(Tag).where(Tag.name == tag_name)
    return db.execute(statement).scalars().first()


def create_tag_by_dict(db: Session, tag_data: dict) -> Tag:
    """创建新标签"""
    # 检查标签名是否已存在
    existing_tag = get_tag_by_name(db, tag_data["name"])
    if existing_tag:
        raise ValueError(f"Tag with name '{tag_data['name']}' already exists")

    tag = Tag(**tag_data)
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag


def create_tag(db: Session, tag_name: str, tag_type: TagType = TagType.USER) -> Tag:
    """创建新标签"""
    tag = Tag(name=tag_name, type=tag_type)
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag


def add_tag_to_word(db: Session, word_id: int, tag_name: str, tag_type: TagType = TagType.USER) -> Optional[Tag]:
    """为单词添加标签"""
    # 检查标签是否存在
    tag = get_tag_by_name(db, tag_name)

    # 如果标签不存在，创建新标签
    if not tag:
        tag = create_tag(db, tag_name, tag_type)

    # 检查是否已关联
    if is_exist_tag_relation(db, word_id, tag_name):
        return tag  # 已存在关联

    # 创建关联
    word_tag = WordTagLink(word_id=word_id, tag_id=tag.id)
    db.add(word_tag)
    db.commit()

    return tag


def remove_tag_from_word(db: Session, word_id: int, tag_name: str) -> bool:
    """从单词移除标签"""
    # 查找标签
    tag = get_tag_by_name(db, tag_name)
    if not tag:
        return False

    # 删除关联
    statement = delete(WordTagLink).where(
        WordTagLink.word_id == word_id,
        WordTagLink.tag_id == tag.id
    )
    db.execute(statement)
    db.commit()

    return True


# Tag 完整 CRUD 操作
def get_all_tags(db: Session, skip: int = 0, limit: int = 100) -> List[Tag]:
    """获取所有标签"""
    statement = select(Tag).offset(skip).limit(limit)
    return db.execute(statement).scalars().all()


def get_tag_by_id(db: Session, tag_id: int) -> Optional[Tag]:
    """通过ID获取标签"""
    return db.get(Tag, tag_id)


def update_tag(db: Session, tag_id: int, tag_data: dict) -> Optional[Tag]:
    """更新标签"""
    tag = db.get(Tag, tag_id)
    if not tag:
        return None

    # 如果修改了名称，检查是否与其他标签冲突
    if "name" in tag_data and tag_data["name"] != tag.name:
        existing_tag = get_tag_by_name(db, tag_data["name"])
        if existing_tag:
            raise ValueError(f"Tag with name '{tag_data['name']}' already exists")

    for field, value in tag_data.items():
        setattr(tag, field, value)

    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag


def delete_tag(db: Session, tag_id: int) -> bool:
    """删除标签（同时删除所有关联关系）"""
    tag = db.get(Tag, tag_id)
    if not tag:
        return False

    # 先删除所有关联关系
    statement = delete(WordTagLink).where(WordTagLink.tag_id == tag_id)
    db.execute(statement)

    # 删除标签
    db.delete(tag)
    db.commit()
    return True


def get_words_by_tag(db: Session, tag_id: int) -> List[Word]:
    """获取拥有指定标签的所有单词"""
    statement = select(Word).join(WordTagLink).where(WordTagLink.tag_id == tag_id)
    return db.execute(statement).scalars().all()


def get_words_by_tag_name(db: Session, tag_name: str) -> List[Word]:
    """通过标签名获取所有相关单词"""
    statement = select(Word).join(WordTagLink).join(Tag).where(Tag.name == tag_name)
    return db.execute(statement).scalars().all()


# ---------- 单词-例句关联操作 ----------
def add_word_to_example(
    db: Session,
    example_id: int,
    word_id: int,
    definition_id: int,
    start_pos: int,
    end_pos: int
) -> ExampleWord:
    """将单词关联到例句，指定释义和位置"""
    # 校验存在性
    example = db.get(Example, example_id)
    word = db.get(Word, word_id)
    definition = db.get(WordDefinition, definition_id)
    if not all([example, word, definition]):
        raise ValueError("例句、单词或释义不存在")

    # 创建关联记录
    link = ExampleWord(
        example_id=example_id,
        word_id=word_id,
        definition_id=definition_id,
        start_pos=start_pos,
        end_pos=end_pos
    )
    db.add(link)
    db.commit()
    db.refresh(link)
    return link


def remove_word_from_example(db: Session, link_id: int) -> bool:
    """移除单词与例句的关联"""
    link = db.get(ExampleWord, link_id)
    if not link:
        return False
    db.delete(link)
    db.commit()
    return True


def update_word_position_in_example(
    db: Session,
    link_id: int,
    start_pos: int,
    end_pos: int
) -> Optional[ExampleWord]:
    """更新单词在例句中的位置"""
    link = db.get(ExampleWord, link_id)
    if not link:
        return None
    link.start_pos = start_pos
    link.end_pos = end_pos
    db.add(link)
    db.commit()
    db.refresh(link)
    return link


# ---------- 查询操作 ----------
def get_examples_by_word(
    db: Session,
    word_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[Example]:
    """获取单词的所有例句（不包含位置和释义信息）"""
    stmt = (
        select(Example)
        .join(ExampleWord, Example.id == ExampleWord.example_id)
        .where(ExampleWord.word_id == word_id)
        .offset(skip)
        .limit(limit)
    )
    return db.execute(stmt).all()


def get_examples_with_word_info(
    db: Session,
    word_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[dict]:
    """
    获取单词的所有例句，并包含单词在例句中的位置及使用的释义。
    返回格式: [
        {
            "example": Example对象,
            "start_pos": int,
            "end_pos": int,
            "definition": WordDefinition对象
        },
        ...
    ]
    """
    stmt = (
        select(Example, ExampleWord, WordDefinition)
        .join(ExampleWord, Example.id == ExampleWord.example_id)
        .join(WordDefinition, ExampleWord.definition_id == WordDefinition.id)
        .where(ExampleWord.word_id == word_id)
        .offset(skip)
        .limit(limit)
    )
    results = db.execute(stmt).all()
    return [
        {
            "example": ex,
            "start_pos": ew.start_pos,
            "end_pos": ew.end_pos,
            "definition": wd
        }
        for ex, ew, wd in results
    ]


def get_examples_by_definition(
    db: Session,
    definition_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[Example]:
    """获取使用了指定释义的所有例句"""
    stmt = (
        select(Example)
        .join(ExampleWord, Example.id == ExampleWord.example_id)
        .where(ExampleWord.definition_id == definition_id)
        .offset(skip)
        .limit(limit)
    )
    return db.execute(stmt).all()


def get_words_in_example(
    db: Session,
    example_id: int
) -> List[dict]:
    """获取例句中的所有单词及其位置和释义"""
    stmt = (
        select(Word, ExampleWord, WordDefinition)
        .join(ExampleWord, Word.id == ExampleWord.word_id)
        .join(WordDefinition, ExampleWord.definition_id == WordDefinition.id)
        .where(ExampleWord.example_id == example_id)
    )
    results = db.execute(stmt).all()
    return [
        {
            "word": w,
            "start_pos": ew.start_pos,
            "end_pos": ew.end_pos,
            "definition": wd
        }
        for w, ew, wd in results
    ]