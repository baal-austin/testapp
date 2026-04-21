# models/word_relation.py
import re
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime

from pydantic import field_validator
from sqlalchemy import Text, Integer, ForeignKey
from sqlmodel import SQLModel, Field, Relationship, Column
from app.models.enums import AccentType, PartOfSpeechAbbr, TagType, FormType
from .book import WordbookWordLink
from .note import NoteWordLink


if TYPE_CHECKING:
    from .relation import WordRelation
    from .note import Note
    from .book import Wordbook
    from .study import UserStudyRecord, UserWordProgress


class ExampleWord(SQLModel, table=True):
    """例句-单词关联表，记录单词在例句中的出现位置及使用的释义"""
    __tablename__ = "example_words"

    id: Optional[int] = Field(default=None, primary_key=True, description="关联记录唯一标识符")
    example_id: int = Field(
        foreign_key="examples.id", nullable=False, description="例句ID"
    )
    word_id: int = Field(
        foreign_key="words.id", nullable=False, description="单词ID"
    )
    definition_id: int = Field(
        foreign_key="word_definitions.id", nullable=False, description="该单词在此例句中使用的释义ID"
    )
    start_pos: int = Field(ge=0, description="单词在例句文本中的起始字符索引")
    end_pos: int = Field(ge=0, description="单词在例句文本中的结束字符索引（不包含）")

    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"onupdate": datetime.utcnow},
        description="更新时间"
    )

    # 关系
    example_rel: "Example" = Relationship(back_populates="words_rel")
    word_rel: "Word" = Relationship(back_populates="example_words_rel")
    definition_rel: "WordDefinition" = Relationship(back_populates="example_words_rel")

class WordTagLink(SQLModel, table=True):
    """单词标签关联表"""
    __tablename__ = "word_tags_link"

    # 使用复合主键
    word_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("words.id", ondelete="CASCADE"),
            primary_key=True
        )
    )
    tag_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("tags.id", ondelete="CASCADE"),
            primary_key=True
        )
    )
    # 时间戳字段
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")


# 单词核心表
class Word(SQLModel, table=True):
    """单词表，存储单词的基本信息"""
    __tablename__ = "words"

    id: Optional[int] = Field(default=None, primary_key=True, description="单词唯一标识符")
    word: str = Field(max_length=100, unique=True, nullable=False, index=True, description="单词原文")
    normalized_word: str = Field(max_length=100, index=True, description="标准化后的单词(小写形式，便于搜索)")
    length: int = Field(ge=1, description="单词长度(字符数)")
    definition_cn: str = Field(max_length=100, description="简单中文释义")
    definition_en: str = Field(max_length=100, description="简单英文释义")
    # pronunciation_us: str = Field(description="美式发音")
    # pronunciation_uk: str = Field(description="英式发音")
    # soundmark_us: str = Field(description="美式音标")
    # soundmark_uk: str = Field(description="英式英标")

    # 统计和元数据
    frequency_rank: Optional[int] = Field(default=None, ge=1, description="词频排名，数值越小表示越常见")
    difficulty_level: Optional[float] = Field(default=None, ge=1, le=5, description="难度等级(1-5)")
    is_common: bool = Field(default=True, description="是否为常用词")
    tags_json: Optional[List[str]] = Field(default=None, sa_column=Column(Text), description="单词标签的JSON字符串")
    etymology: Optional[str] = Field(default=None, description="词源信息")
    description: str = Field(default="", description="描述")

    # 用户互动统计
    view_count: int = Field(default=0, ge=0, description="浏览数")
    known_count: int = Field(default=0, ge=0, description="认识人数统计")
    unknown_count: int = Field(default=0, ge=0, description="不认识人数统计")
    uncertain_count: int = Field(default=0, ge=0, description="模糊认识人数统计")

    # 时间戳字段
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"onupdate": datetime.utcnow},
        description="更新时间"
    )

    # 关系
    # 强依赖关系 - 设置级联删除
    # 不设置 级联删除
    # 多对多关系的中间表（如词库-单词映射）
    # 与其他实体的关联（如笔记、用户收藏等）
    definitions_rel: List["WordDefinition"] = Relationship(
        back_populates="word_rel",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan",
            "lazy": "selectin"
        }
    )
    # 新增 example_words_rel
    example_words_rel: List["ExampleWord"] = Relationship(
        back_populates="word_rel",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "lazy": "selectin"}
    )
    # 为了方便直接获取例句，可以添加 property
    @property
    def examples(self) -> List["Example"]:
        """获取该单词关联的所有例句（通过 ExampleWord）"""
        return [ew.example_rel for ew in self.example_words_rel]

    pronunciations_rel: List["WordPronunciation"] = Relationship(
        back_populates="word_rel",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan",
            "lazy": "selectin"
        }
    )
    forms_rel: List["WordForm"] = Relationship(
        back_populates="word_rel",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan",
            "lazy": "selectin"
        }
    )
    tags_rel: List["Tag"] = Relationship(
        back_populates="words_rel",
        link_model=WordTagLink
    )
    # 笔记相关关系
    notes_rel: List["Note"] = Relationship(
        back_populates="words_rel",
        link_model=NoteWordLink
    )
    # 词库相关关系
    wordbooks_rel: List["Wordbook"] = Relationship(
        back_populates="words_rel",
        link_model=WordbookWordLink
    )
    # 关系相关关系
    source_relations_rel: List["WordRelation"] = Relationship(
        back_populates="source_word_rel",
        sa_relationship_kwargs={
            "foreign_keys": "[WordRelation.source_word_id]",
            "lazy": "selectin"
        }
    )

    target_relations_rel: List["WordRelation"] = Relationship(
        back_populates="target_word_rel",
        sa_relationship_kwargs={
            "foreign_keys": "[WordRelation.target_word_id]",
            "lazy": "selectin"
        }
    )
    # 学习相关关系
    study_records_rel: List["UserStudyRecord"] = Relationship(back_populates="word_rel")
    word_progress_rel: List["UserWordProgress"] = Relationship(back_populates="word_rel")
    # Pydantic验证器
    @field_validator('normalized_word', mode='before')
    @classmethod
    def set_normalized_word(cls, v, values):
        """自动设置标准化单词"""
        if 'word' in values and values['word']:
            return values['word'].lower()
        return v

    @field_validator('length', mode='before')
    @classmethod
    def set_length(cls, v, values):
        """自动设置单词长度"""
        if 'word' in values and values['word']:
            return len(values['word'])
        return v

    @field_validator('word')
    @classmethod
    def validate_word_format(cls, v):
        """验证单词格式"""
        if not re.match(r'^[a-zA-Z\-.\']+$', v):
            raise ValueError('单词只能包含字母、连字符、点和撇号')
        return v

    @property
    def total_attempts(self) -> int:
        """总尝试次数"""
        return self.known_count + self.unknown_count + self.uncertain_count

    @property
    def calculated_difficulty_level(self) -> int:
        """计算难度等级（1-5）"""
        if self.total_attempts < 5:  # 数据量不足
            return 3  # 默认中等难度

        error_rate = self.unknown_count / self.total_attempts
        return max(1, min(5, round(1 + 4 * error_rate)))

    @property
    def accuracy_rate(self) -> float:
        """正确率（0.0-1.0）"""
        if self.total_attempts == 0:
            return 0.0
        correct = self.known_count + self.uncertain_count * 0.5
        return round(correct / self.total_attempts, 2)

    @property
    def tags(self) -> List["Tag"]:
        """便捷属性：直接获取标签列表"""
        return [link.tag_rel for link in self.tag_links_rel]


class WordDefinition(SQLModel, table=True):
    """单词定义表，存储单词的不同词性和定义"""
    __tablename__ = "word_definitions"

    id: Optional[int] = Field(default=None, primary_key=True, description="释义唯一标识符")
    word_id: int = Field(foreign_key="words.id", description="关联的单词ID")
    part_of_speech: PartOfSpeechAbbr = Field(max_length=20, nullable=False, description="词性")
    definition: Optional[str] = Field(default=None, max_length=50, description="英文释义")
    definition_cn: str = Field(max_length=50, nullable=False, description="中文释义")
    order: int = Field(default=1, ge=1, description="释义显示顺序")
    domains_json: Optional[str] = Field(default=None, sa_column=Column(Text),
                                        description="适用领域的JSON字符串(如:医学,法律,计算机等)")
    example_usage: Optional[str] = Field(default=None, description="用法示例")

    # 时间戳字段
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"onupdate": datetime.utcnow},
        description="更新时间"
    )

    # 定义关系
    word_rel: "Word" = Relationship(back_populates="definitions_rel")


class Example(SQLModel, table=True):
    """例句表，存储单词的用法例句"""
    __tablename__ = "examples"

    id: Optional[int] = Field(default=None, primary_key=True, description="例句唯一标识符")

    sentence: str = Field(max_length=8000, nullable=False, description="例句原文")
    translation: str = Field(max_length=8000, nullable=False, description="例句翻译")
    source: Optional[str] = Field(default=None, description="例句来源(如词典名称、文学作品等)")
    context: Optional[str] = Field(default=None, description="例句上下文信息")
    voice: str = Field(max_length=100, nullable=False, description="语音")
    # 时间戳字段
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"onupdate": datetime.utcnow},
        description="更新时间"
    )
    # 关系
    words_rel: List["ExampleWord"] = Relationship(
        back_populates="example_rel",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "lazy": "selectin"}
    )
    @property
    def word_list(self) -> List["Word"]:
        """获取例句中的所有单词"""
        return [ew.word_rel for ew in self.words_rel]


class WordForm(SQLModel, table=True):
    """单词形式表，存储单词的不同语法形式"""
    __tablename__ = "word_forms"

    id: Optional[int] = Field(default=None, primary_key=True, description="单词形式唯一标识符")
    word_id: int = Field(foreign_key="words.id", description="关联的单词ID")
    form_type: FormType = Field(max_length=50, nullable=False, description="形式类型(如:过去式,过去分词等)")
    form_word: str = Field(max_length=100, nullable=False, description="变形后的单词")

    # 时间戳字段
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"onupdate": datetime.utcnow},
        description="更新时间"
    )

    # 定义关系
    word_rel: "Word" = Relationship(back_populates="forms_rel")


class WordPronunciation(SQLModel, table=True):
    """发音表，存储单词的不同口音发音"""
    __tablename__ = "word_pronunciations"

    id: Optional[int] = Field(default=None, primary_key=True, description="发音记录唯一标识符")

    word_id: int = Field(foreign_key="words.id", description="关联的单词ID")
    accent: AccentType = Field(description="发音口音")
    audio_url: str = Field(unique=True, nullable=False, description="发音音频文件URL")
    phonetic: Optional[str] = Field(default=None, description="音标表示")
    voice_actor: Optional[str] = Field(default=None, description="配音演员")
    audio_quality: Optional[str] = Field(default=None, description="音频质量(如:标准,高清)")

    # 定义关系
    word_rel: "Word" = Relationship(back_populates="pronunciations_rel")

    # @field_validator('audio_url')
    # @classmethod
    # def validate_audio_url(cls, v):
    #     """验证音频URL格式"""
    #     if v is None:
    #         return None
    #     if not re.match(r'^https?://.+\.(mp3|wav|ogg|m4a)$', v):
    #         raise ValueError('音频链接必须是有效的MP3、WAV、OGG或M4A URL')
    #     return v


class Tag(SQLModel, table=True):
    """标签表，存储标签名"""
    __tablename__ = "tags"

    id: Optional[int] = Field(default=None, primary_key=True, description="标签唯一标识符")
    name: str = Field(max_length=50, unique=True, nullable=False, description="标签名称")
    type: TagType = Field(default=TagType.SYSTEM, nullable=False, description="标签类型(system/user)")
    description: Optional[str] = Field(default=None, description="标签描述")

    # 时间戳字段
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"onupdate": datetime.utcnow},
        description="更新时间"
    )

    # 关系
    words_rel: List["Word"] = Relationship(back_populates="tags_rel",link_model=WordTagLink)


