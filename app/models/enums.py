from enum import Enum


class PartOfSpeech(str, Enum):
    """词性枚举，定义单词的不同语法类别"""
    NOUN = "noun"  # 名词
    VERB = "verb"  # 动词
    ADJECTIVE = "adjective"  # 形容词
    ADVERB = "adverb"  # 副词
    PREPOSITION = "preposition"  # 介词
    CONJUNCTION = "conjunction"  # 连词
    PRONOUN = "pronoun"  # 代词
    INTERJECTION = "interjection"  # 感叹词
    DETERMINER = "determiner"  # 限定词
    NUM = "num"  # 数词
    ARTICLE = "article."  # 冠词


class PartOfSpeechAbbr(str, Enum):
    """词性枚举，定义单词的不同语法类别"""
    NOUN = "n."  # 名词
    TRANS_VERB = "vt."  # 及物动词
    INTRANS_VERB = "vi."  # 不及物动词
    VERB = "v."  # 动词
    ADJECTIVE = "adj."  # 形容词
    ADVERB = "adverb"  # 副词
    PREPOSITION = "prep."  # 介词
    CONJUNCTION = "conj."  # 连词
    PRONOUN = "pron."  # 代词
    INTERJECTION = "interj."  # 感叹词
    NUM = "num。"  # 限定词
    ARTICLE = "art."  # 冠词


class FormType(str, Enum):
    """单词形式枚举，定义单词的不同语法形式"""
    BASE_FORM = "BASE_FORM"  # 基础形式(原形)
    THIRD_PERSON = "THIRD_PERSON"  # 第三人称单数现在时
    PAST_TENSE = "PAST_TENSE"  # 过去式
    PAST_PARTICIPLE = "PAST_PARTICIPLE"  # 过去分词
    PRESENT_PARTICIPLE = "PRESENT_PARTICIPLE"  # 现在分词/动名词
    PLURAL_FORM = "PLURAL_FORM"  # 复数形式
    COMPARATIVE = "COMPARATIVE"  # 比较级
    SUPERLATIVE = "SUPERLATIVE"  # 最高级
    POSSESSIVE = "POSSESSIVE"  # 所有格形式
    GERUND = "GERUND"  # 动名词
    INFINITIVE = "INFINITIVE"  # 不定式


class AccentType(str, Enum):
    """口音类型枚举，定义不同地区的发音口音"""
    US = "us"  # 美式英语
    UK = "uk"  # 英式英语
    AU = "au"  # 澳大利亚英语
    CA = "ca"  # 加拿大英语


class RelationCategory(str, Enum):
    """关系类别枚举"""
    SEMANTIC = "semantic"  # 语义关系
    FORMAL = "formal"  # 形式关系
    MORPHEMIC = "morphemic"  # 词素关系（构词成分）
    MORPHOLOGICAL = "morphological"  # 形态关系
    ASSOCIATIVE = "associative"  # 联想关系


class RelationType(str, Enum):
    """单词关系类型枚举，定义单词之间的不同语义关系"""
    # ==================== 语义关系 (基于含义) ====================
    # 核心语义关系
    SYNONYM = "synonym"  # 同义词 happy↔ joyful（快乐的） big↔ large（大的）
    ANTONYM = "antonym"  # 反义词 hot↔ cold（热/冷） up↔ down（上/下）
    # PARENT_CHILD = "parent_child"  # 父子关系（类属层级） apple↔ fruit（苹果/水果）
    # PART_WHOLE = "part_whole"  # 部分整体关系  wheel↔ car（轮子→汽车）
    SISTER_TERM = "sister_term"  # 同位词/兄弟概念 apple↔ orange（苹果↔橙子） car↔ bus（汽车↔公交车）
    HYPERNYM = "hypernym"  # 上位词/父类词 apple→ fruit（苹果→水果）car→ vehicle（汽车→车辆）
    HYPONYM = "hyponym"  # 下位词/子类词 fruit→ apple（水果→苹果） animal→ dog（动物→狗）
    HOLONYM = "holonym"  # 整体词 wheel→ car（轮子→汽车） chapter→ book（章节→书）
    MERONYM = "meronym"  # 部分词 car→ wheel（汽车→轮子） book→ chapter（书→章节）

    # ==================== 形式关系 (基于拼写、发音、构词法) ====================
    # 音形关系
    HOMOPHONE = "homophone"  # 同音异形异义词 see↔ sea（看见/大海） right↔ write（正确/写）
    HOMONYM = "homonym"  # 同形异义词 see↔ sea（看见/大海）
    PARONYM = "paronym"  # 近音词 affect↔ effect（影响/效果）accept↔ except（接受/除了）
    SIMILAR = "similar"  # 拼写相似词 though↔ through（虽然/通过）quiet↔ quite（安静的/相当）

    # 构词关系
    ABBREVIATION = "abbreviation"  # 缩写/简写关系 advertisement↔ ad（广告） photograph↔ photo（照片）
    VARIANT = "variant"  # 变体形式 color↔ colour（颜色，美式/英式） realize↔ realise（实现）

    # ==================== 形态关系 (基于单词的语法形态变化) ====================
    # 动词形态
    BASE_FORM = "base_form"  # 基础形式(原形) goes（三单）→ go（原形）
    THIRD_PERSON = "third_person"  # 第三人称单数现在时 go→ goes
    PAST_TENSE = "past_tense"  # 过去式 go→ went
    PAST_PARTICIPLE = "past_participle"  # 过去分词 go→ gone
    PRESENT_PARTICIPLE = "present_participle"  # 现在分词/动名词 run→ running

    # 名词形态
    PLURAL_FORM = "plural_form"  # 复数形式 book→ books child→ children
    POSSESSIVE = "possessive"  # 所有格形式 I → my, he → his, children→ children's ,teachers→ teachers'

    # 形容词/副词形态
    COMPARATIVE = "comparative"  # 比较级 big→ bigger
    SUPERLATIVE = "superlative"  # 最高级 big→ biggest

    ## 词性转换
    TO_NOUN = "to_noun"  # 转换为名词 happy(adj.) → happiness(n.) 快乐→幸福感
    TO_VERB = "to_verb"  # 转换为动词 simple(adj.) → simplify(v.) 简单→简化
    TO_ADJ = "to_adj"  # 转换为形容词 beauty(n.) → beautiful(adj.) 美丽→美丽的
    TO_ADV = "to_adv"  # 转换为副词 quick(adj.) → quickly(adv.) 快→快速地

    DERIVATION = "derivation"  # 派生关系

    # ==================== 词素关系 ====================
    ROOT_RELATION = "root_relation"  # 词根关系 "passive" ↔ "pass"
    SUFFIX_RELATION = "suffix_relation"  # 后缀关系 "-ive" ↔ "pass"
    PREFIX_RELATION = "prefix_relation"  # 前缀关系 “un-" ↔ "unhappy"

    # ==================== 联想与用法关系 (基于经验、语境和自定义) ====================
    # 搭配关系
    COLLOCATION = "collocation"  # 固定搭配 make + decision 习惯性共现
    COMPOUND = "compound"  # 复合词关系(如"car door") 形成新词汇项
    PHRASE_COMPOSITION = "phrase_composition"  # 短语构成关系 in front of 固定多词组合
    IDIOM_COMPONENT = "idiom_component"  # 习语构成成分 kick the bucket 整体意义隐喻化
    SEMANTIC_ROLE = "semantic_role"  # 角色关系 buyer- buy（施事关系），book- read（受事关系）
    CONTEXTUAL = "contextual"  # 上下文关联关系 beach- sand，hospital- doctor

    CUSTOM = "custom"  # 自定义关系


class ContributionType(str, Enum):
    """用户贡献类型枚举，定义用户可以进行的贡献类型"""
    ADD_WORD = "add_word"  # 添加单词
    UPDATE_WORD = "update_word"  # 更新单词
    ADD_RELATION = "add_relation"  # 添加关系
    UPDATE_RELATION = "update_relation"  # 更新关系


class ContributionStatus(str, Enum):
    """贡献状态枚举，定义用户贡献的审核状态"""
    PENDING = "pending"  # 待审核
    APPROVED = "approved"  # 已批准
    REJECTED = "rejected"  # 已拒绝


class LanguageCode(str, Enum):
    """界面语言代码枚举"""
    ZH_CN = "zh-CN"  # 简体中文
    EN_US = "en-US"  # 英语（美国）
    EN_UK = "en-UK"  # 英语（英国）
    JA_JP = "ja-JP"  # 日语
    KO_KR = "ko-KR"  # 韩语


class TagType(str, Enum):
    """标签类型枚举"""
    SYSTEM = "system"  # 系统标签
    USER = "user"  # 用户自定义标签


# class NoteType(str, Enum):
#     """笔记类型枚举"""
#     WORD = "word"  # 单词笔记
#     RELATION = "relation"  # 关系笔记
#     GENERAL = "general"  # 通用笔记


class NoteVisibility(str, Enum):
    """笔记可见性枚举"""
    PRIVATE = "private"  # 仅自己可见
    PUBLIC = "public"  # 公开可见
    SHARED = "shared"  # 分享给特定用户


class UserStatus(str, Enum):
    """用户状态枚举"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class AuthProvider(str, Enum):
    """认证提供商枚举"""
    EMAIL = "email"  # 邮箱密码登录
    PHONE = "phone"  # 手机号登录
    WECHAT = "wechat"  # 微信登录
    QQ = "qq"  # QQ登录
