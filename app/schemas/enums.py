from enum import Enum
import re


class LoginType(str, Enum):
    EMAIL = "email"
    PHONE = "phone"
    WECHAT = "wechat"
    QQ = "qq"


class PartOfSpeech(str, Enum):
    NOUN = "noun"
    VERB = "verb"
    ADJECTIVE = "adjective"
    ADVERB = "adverb"
    PREPOSITION = "preposition"
    CONJUNCTION = "conjunction"
    PRONOUN = "pronoun"
    INTERJECTION = "interjection"
    DETERMINER = "determiner"
    PHRASAL_VERB = "phrasal_verb"
    IDIOM = "idiom"


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
    US = "us"
    UK = "uk"
    AU = "au"
    CA = "ca"


class RelationType(str, Enum):
    # ==================== 语义关系 (基于含义) ====================
    ## 核心语义关系
    SYNONYM = "synonym"  # 同义词
    ANTONYM = "antonym"  # 反义词
    HYPERNYM = "hypernym"  # 上位词/父类词
    HYPONYM = "hyponym"  # 下位词/子类词
    HOLONYM = "holonym"  # 整体词
    MERONYM = "meronym"  # 部分词
    SISTER_TERM = "sister_term"  # 同位词/兄弟概念

    # ==================== 形式关系 (基于拼写、发音、构词法) ====================
    ## 音形关系
    HOMOPHONE = "homophone"  # 同音异形异义词
    HOMONYM = "homonym"  # 同形异义词
    PARONYM = "paronym"  # 近音词
    SIMILAR = "similar"  # 拼写相似词

    ## 构词关系
    DERIVATION = "derivation"  # 派生关系
    ABBREVIATION = "abbreviation"  # 缩写/简写关系
    VARIANT = "variant"  # 变体形式

    # ==================== 形态关系 (基于单词的语法形态变化) ====================
    ## 动词形态
    BASE_FORM = "base_form"  # 基础形式(原形)
    THIRD_PERSON = "third_person"  # 第三人称单数现在时
    PAST_TENSE = "past_tense"  # 过去式
    PAST_PARTICIPLE = "past_participle"  # 过去分词
    PRESENT_PARTICIPLE = "present_participle"  # 现在分词/动名词

    ## 名词形态
    PLURAL_FORM = "plural_form"  # 复数形式
    POSSESSIVE = "possessive"  # 所有格形式

    ## 形容词/副词形态
    COMPARATIVE = "comparative"  # 比较级
    SUPERLATIVE = "superlative"  # 最高级

    ## 词性转换
    TO_NOUN = "to_noun"  # 转换为名词
    TO_VERB = "to_verb"  # 转换为动词
    TO_ADJ = "to_adj"  # 转换为形容词
    TO_ADV = "to_adv"  # 转换为副词

    # ==================== 联想与用法关系 (基于经验、语境和自定义) ====================
    ## 搭配关系
    COLLOCATION = "collocation"  # 固定搭配
    COMPOUND = "compound"  # 复合词关系(如"car door")
    PHRASE_COMPOSITION = "phrase_composition"  # 短语构成关系

    ## 扩展关系
    RELATED = "related"  # 相关词(宽泛语境关联)
    IDIOM_COMPONENT = "idiom_component"  # 习语构成成分
    SEMANTIC_ROLE = "semantic_role"  # 语义角色关系
    CONTEXTUAL = "contextual"  # 上下文关联关系
    CUSTOM = "custom"  # 自定义关系


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


class TagType(str, Enum):
    """标签类型枚举"""
    SYSTEM = "system"  # 系统标签
    USER = "user"  # 用户自定义标签
