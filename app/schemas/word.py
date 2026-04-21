# app/schemas/word.py
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime
from app.schemas.enums import AccentType, PartOfSpeechAbbr, TagType


# 基础Schemas
from app.schemas.enums import FormType


class WordDefinitionBase(BaseModel):
    part_of_speech: PartOfSpeechAbbr
    definition: str
    definition_cn: str
    order: int = Field(ge=1, default=1)
    domains_json: Optional[str] = None
    example_usage: Optional[str] = None


class ExampleBase(BaseModel):
    sentence: str
    translation: str
    start_pos: int
    end_pos: int
    source: Optional[str] = None
    context: Optional[str] = None


class WordFormBase(BaseModel):
    form_type: FormType
    form_word: str


class WordPronunciationBase(BaseModel):
    accent: AccentType
    audio_url: str
    phonetic: Optional[str] = None
    voice_actor: Optional[str] = None
    audio_quality: Optional[str] = None


class TagBase(BaseModel):
    name: str
    type: TagType = TagType.SYSTEM
    description: Optional[str] = None


# 创建Schemas
class WordDefinitionCreate(WordDefinitionBase):
    pass


class ExampleCreate(ExampleBase):
    pass


class WordFormCreate(WordFormBase):
    pass


class WordPronunciationCreate(WordPronunciationBase):
    pass


class TagCreate(TagBase):
    pass


# 更新Schemas
class WordDefinitionUpdate(BaseModel):
    part_of_speech: Optional[PartOfSpeechAbbr] = None
    definition: Optional[str] = None
    definition_cn: Optional[str] = None
    order: Optional[int] = Field(None, ge=1)
    domains_json: Optional[str] = None
    example_usage: Optional[str] = None


class ExampleUpdate(BaseModel):
    sentence: Optional[str] = None
    translation: Optional[str] = None
    source: Optional[str] = None
    context: Optional[str] = None


class WordFormUpdate(BaseModel):
    form_type: Optional[str] = None
    form_word: Optional[str] = None


class WordPronunciationUpdate(BaseModel):
    accent: Optional[AccentType] = None
    audio_url: Optional[str] = None
    phonetic: Optional[str] = None
    voice_actor: Optional[str] = None
    audio_quality: Optional[str] = None


class TagUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[TagType] = None
    description: Optional[str] = None


# 读取Schemas
class WordDefinitionRead(WordDefinitionBase):
    id: int
    word_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ExampleRead(ExampleBase):
    id: int
    word_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WordFormRead(WordFormBase):
    id: int
    word_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WordPronunciationRead(WordPronunciationBase):
    id: int
    word_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TagRead(TagBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# 单词的Schemas
class WordBase(BaseModel):
    word: str
    frequency_rank: Optional[int] = None
    difficulty_level: Optional[float] = Field(None, ge=1, le=5)
    is_common: bool = True
    etymology: Optional[str] = None
    description: str = ""


class WordCreate(WordBase):
    definitions: List[WordDefinitionCreate] = []
    examples: List[ExampleCreate] = []
    forms: List[WordFormCreate] = []
    pronunciations: List[WordPronunciationCreate] = []
    tags: List[TagCreate] = []  # 标签名称列表


class WordUpdate(BaseModel):
    word: Optional[str] = None
    frequency_rank: Optional[int] = None
    difficulty_level: Optional[float] = Field(None, ge=1, le=5)
    is_common: Optional[bool] = None
    etymology: Optional[str] = None
    description: Optional[str] = None


class WordRead(WordBase):
    id: int
    normalized_word: str
    length: int
    view_count: int
    known_count: int
    unknown_count: int
    uncertain_count: int
    created_at: datetime
    updated_at: datetime
    tags: List[str] = []  # 标签名称列表

    definitions: List[WordDefinitionRead] = []
    examples: List[ExampleRead] = []
    forms: List[WordFormRead] = []
    pronunciations: List[WordPronunciationRead] = []

    class Config:
        from_attributes = True


# 用于搜索和列表的简化Schema
class WordSimple(BaseModel):
    id: int
    word: str
    normalized_word: str
    length: int
    frequency_rank: Optional[int]
    difficulty_level: Optional[float]
    is_common: bool

    class Config:
        from_attributes = True


# 用于批量操作的Schemas
class BulkWordCreate(BaseModel):
    words: List[WordCreate]


class BulkWordUpdate(BaseModel):
    updates: List[Dict[str, Any]]  # 包含word_text和update_data的列表


class BulkWordDelete(BaseModel):
    word_texts: List[str]


# 用于统计和报告的Schemas
class WordStats(BaseModel):
    total_words: int
    common_words: int
    average_difficulty: float
    total_views: int
    total_known: int
    total_unknown: int
    total_uncertain: int


class WordFrequencyReport(BaseModel):
    word: str
    frequency_rank: Optional[int]
    view_count: int
    known_count: int
    unknown_count: int
    uncertain_count: int
    accuracy_rate: float


# 用于搜索建议的Schema
class SearchSuggestion(BaseModel):
    word: str
    normalized_word: str
    length: int

    class Config:
        from_attributes = True


# 用于API响应的通用Schema
class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None


# 用于分页结果的Schema
class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    size: int
    pages: int


# 用于错误响应的Schema
class ErrorResponse(BaseModel):
    detail: str
    code: Optional[str] = None


# 用于验证单词格式的Schema
class WordValidation(BaseModel):
    word: str
    is_valid: bool
    normalized_word: str
    suggestions: Optional[List[str]] = None


