from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime, date, time
from enum import Enum
from pydantic import field_validator, model_validator

if TYPE_CHECKING:
    from .user import User
    from .word import Word
    from .book import Wordbook


class LearningStatus(str, Enum):
    """学习状态"""
    NEW = "new"  # 新单词（未学习）
    LEARNING = "learning"  # 学习中
    REVIEWING = "reviewing"  # 复习中
    MASTERED = "mastered"  # 已掌握


class AnswerType(str, Enum):
    """回答类型"""
    KNOWN = "known"  # 认识
    UNKNOWN = "unknown"  # 不认识
    UNCERTAIN = "uncertain"  # 模糊


class StudyMode(str, Enum):
    """学习模式"""
    WORD_TO_DEFINITION = "word_to_definition"  # 单词->释义
    DEFINITION_TO_WORD = "definition_to_word"  # 释义->单词
    LISTENING = "listening"  # 听力
    SPELLING = "spelling"  # 拼写


class UserLearningPlan(SQLModel, table=True):
    """用户学习计划表"""
    __tablename__ = "user_learning_plans"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True, description="用户ID")
    wordbook_id: int = Field(foreign_key="wordbooks.id", description="当前学习的词库ID")
    name: str = Field(max_length=100, description="计划名称")

    # 学习目标设置
    daily_new_words: int = Field(default=20, ge=1, le=100, description="每日新学单词数")
    daily_review_words: int = Field(default=30, ge=1, le=200, description="每日复习单词数")

    # 学习状态
    is_active: bool = Field(default=True, description="是否激活")
    current_streak: int = Field(default=0, description="连续学习天数")
    total_study_days: int = Field(default=0, description="总学习天数")

    # 进度统计
    total_words: int = Field(default=0, description="词库总单词数")
    learned_words: int = Field(default=0, description="已学单词数")
    mastered_words: int = Field(default=0, description="已掌握单词数")

    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"onupdate": datetime.utcnow},
        description="更新时间"
    )

    # 关系
    user_rel: "User" = Relationship(back_populates="learning_plans_rel")
    wordbook_rel: "Wordbook" = Relationship(back_populates="learning_plans_rel")
    daily_tasks_rel: List["UserDailyTask"] = Relationship(back_populates="learning_plan_rel")
    word_progress_rel: List["UserWordProgress"] = Relationship(back_populates="learning_plan_rel")
    study_sessions_rel: List["UserStudySession"] = Relationship(back_populates="learning_plan_rel")
    study_records_rel: List["UserStudyRecord"] = Relationship(back_populates="learning_plan_rel")
    # 计算方法
    def calculate_mastery_rate(self) -> float:
        """计算掌握率"""
        if self.total_words == 0:
            return 0.0
        return round(self.mastered_words / self.total_words, 2)

    def calculate_learning_progress(self) -> float:
        """计算学习进度"""
        if self.total_words == 0:
            return 0.0
        return round(self.learned_words / self.total_words, 2)

    def update_streak(self, studied_today: bool) -> None:
        """更新连续学习天数"""
        if studied_today:
            self.current_streak += 1
            if self.current_streak > self.total_study_days:
                self.total_study_days = self.current_streak
        else:
            self.current_streak = 0


class UserDailyTask(SQLModel, table=True):
    """用户每日学习任务表"""
    __tablename__ = "user_daily_tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True, description="用户ID")
    learning_plan_id: int = Field(foreign_key="user_learning_plans.id", description="学习计划ID")
    task_date: date = Field(default_factory=date.today, index=True, description="任务日期")

    # 任务设置
    target_new_words: int = Field(default=0, description="目标新学单词数")
    target_review_words: int = Field(default=0, description="目标复习单词数")

    # 完成情况
    completed_new_words: int = Field(default=0, description="已完成新学单词数")
    completed_reviews: int = Field(default=0, description="已完成复习单词数")
    is_completed: bool = Field(default=False, description="是否完成当日任务")

    # 学习统计
    study_duration: int = Field(default=0, description="学习时长(分钟)")
    accuracy_rate: float = Field(default=0.0, ge=0.0, le=1.0, description="正确率")

    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"onupdate": datetime.utcnow},
        description="更新时间"
    )

    # 关系
    user_rel: "User" = Relationship(back_populates="daily_tasks_rel")
    learning_plan_rel: "UserLearningPlan" = Relationship(back_populates="daily_tasks_rel")
    study_sessions_rel: List["UserStudySession"] = Relationship(back_populates="daily_task_rel")
    study_records_rel: List["UserStudyRecord"] = Relationship(back_populates="daily_task_rel")

    # Pydantic验证器
    @field_validator('accuracy_rate')
    @classmethod
    def validate_accuracy_rate(cls, v: float) -> float:
        """验证正确率范围"""
        if not 0.0 <= v <= 1.0:
            raise ValueError('正确率必须在0.0到1.0之间')
        return round(v, 2)

    @field_validator('task_date')
    @classmethod
    def validate_task_date(cls, v: date) -> date:
        """验证任务日期不能是未来日期"""
        if v > date.today():
            raise ValueError('任务日期不能是未来日期')
        return v

    # 计算方法
    def calculate_completion_rate(self) -> float:
        """计算任务完成率"""
        total_target = self.target_new_words + self.target_review_words
        total_completed = self.completed_new_words + self.completed_reviews

        if total_target == 0:
            return 0.0
        return round(total_completed / total_target, 2)

    def check_completion(self) -> bool:
        """检查是否完成任务"""
        new_completed = self.completed_new_words >= self.target_new_words
        review_completed = self.completed_reviews >= self.target_review_words
        self.is_completed = new_completed and review_completed
        return self.is_completed

    def calculate_remaining_words(self) -> dict:
        """计算剩余单词数"""
        return {
            "new_words": max(0, self.target_new_words - self.completed_new_words),
            "review_words": max(0, self.target_review_words - self.completed_reviews)
        }


class UserStudySession(SQLModel, table=True):
    """用户学习会话表"""
    __tablename__ = "user_study_sessions"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True, description="用户ID")
    learning_plan_id: int = Field(foreign_key="user_learning_plans.id", description="学习计划ID")
    daily_task_id: int = Field(foreign_key="user_daily_tasks.id", description="每日任务ID")

    # 会话信息
    session_type: str = Field(description="学习类型: new_words, review, mixed")
    study_mode: StudyMode = Field(default=StudyMode.WORD_TO_DEFINITION, description="学习模式")
    start_time: datetime = Field(default_factory=datetime.utcnow, description="开始时间")
    end_time: Optional[datetime] = Field(default=None, description="结束时间")
    duration: int = Field(default=0, description="持续时间(秒)")

    # 学习统计
    total_words: int = Field(default=0, description="学习单词总数")
    completed_words: int = Field(default=0, description="完成单词数")
    correct_answers: int = Field(default=0, description="正确回答数")
    wrong_answers: int = Field(default=0, description="错误回答数")
    accuracy_rate: float = Field(default=0.0, ge=0.0, le=1.0, description="正确率")

    # 会话状态
    is_completed: bool = Field(default=False, description="是否完成")

    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")

    # 关系
    user_rel: "User" = Relationship(back_populates="study_sessions_rel")
    learning_plan_rel: "UserLearningPlan" = Relationship(back_populates="study_sessions_rel")
    daily_task_rel: "UserDailyTask" = Relationship(back_populates="study_sessions_rel")
    study_records_rel: List["UserStudyRecord"] = Relationship(back_populates="study_session_rel")

    # Pydantic验证器
    @field_validator('accuracy_rate')
    @classmethod
    def validate_accuracy_rate(cls, v: float) -> float:
        """验证正确率范围"""
        if not 0.0 <= v <= 1.0:
            raise ValueError('正确率必须在0.0到1.0之间')
        return round(v, 2)

    @field_validator('duration')
    @classmethod
    def validate_duration(cls, v: int) -> int:
        """验证学习时长"""
        if v < 0:
            raise ValueError('学习时长不能为负数')
        return v

    # 计算方法
    def calculate_accuracy(self) -> float:
        """计算正确率"""
        total_answers = self.correct_answers + self.wrong_answers
        if total_answers > 0:
            self.accuracy_rate = round(self.correct_answers / total_answers, 2)
        else:
            self.accuracy_rate = 0.0
        return self.accuracy_rate

    def end_session(self) -> None:
        """结束会话"""
        self.end_time = datetime.utcnow()
        if self.start_time and self.end_time:
            self.duration = int((self.end_time - self.start_time).total_seconds())
        self.is_completed = True

    def calculate_completion_rate(self) -> float:
        """计算会话完成率"""
        if self.total_words == 0:
            return 0.0
        return round(self.completed_words / self.total_words, 2)


class UserStudyRecord(SQLModel, table=True):
    """用户学习记录表"""
    __tablename__ = "user_study_records"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True, description="用户ID")
    word_id: int = Field(foreign_key="words.id", index=True, description="单词ID")
    study_session_id: int = Field(foreign_key="user_study_sessions.id", description="学习会话ID")
    daily_task_id: int = Field(foreign_key="user_daily_tasks.id", description="每日任务ID")
    learning_plan_id: int = Field(foreign_key="user_learning_plans.id", description="学习计划ID")

    # 学习信息
    study_mode: StudyMode = Field(description="学习模式")
    answer_type: AnswerType = Field(description="回答类型")
    is_correct: bool = Field(description="是否正确")
    response_time: int = Field(default=0, ge=0, description="响应时间(毫秒)")

    # 学习内容
    question: str = Field(description="问题内容")
    user_answer: Optional[str] = Field(default=None, description="用户答案")
    correct_answer: str = Field(description="正确答案")
    options_shown: Optional[str] = Field(default=None, description="显示的选项(JSON格式)")

    # 难度评估
    difficulty_level: int = Field(default=1, ge=1, le=5, description="难度等级")
    confidence_level: int = Field(default=3, ge=1, le=5, description="自信程度")

    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")

    # 关系
    user_rel: "User" = Relationship(back_populates="study_records_rel")
    word_rel: "Word" = Relationship(back_populates="study_records_rel")
    study_session_rel: "UserStudySession" = Relationship(back_populates="study_records_rel")
    daily_task_rel: "UserDailyTask" = Relationship(back_populates="study_records_rel")
    learning_plan_rel: "UserLearningPlan" = Relationship(back_populates="study_records_rel")

    # Pydantic验证器
    @field_validator('response_time')
    @classmethod
    def validate_response_time(cls, v: int) -> int:
        """验证响应时间"""
        if v < 0:
            raise ValueError('响应时间不能为负数')
        return v

    @field_validator('difficulty_level', 'confidence_level')
    @classmethod
    def validate_level_range(cls, v: int) -> int:
        """验证难度和自信程度范围"""
        if not 1 <= v <= 5:
            raise ValueError('难度和自信程度必须在1-5之间')
        return v


class UserWordProgress(SQLModel, table=True):
    """用户单词进度表"""
    __tablename__ = "user_word_progress"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True, description="用户ID")
    word_id: int = Field(foreign_key="words.id", index=True, description="单词ID")
    learning_plan_id: int = Field(foreign_key="user_learning_plans.id", description="学习计划ID")

    # 学习状态
    status: LearningStatus = Field(default=LearningStatus.NEW, description="学习状态")
    familiarity: int = Field(default=0, ge=0, le=100, description="熟悉程度(0-100)")

    # 间隔重复算法参数 (SM-2算法)
    ease_factor: float = Field(default=2.5, ge=1.3, le=3.0, description="简易因子")
    interval: int = Field(default=0, description="间隔天数")
    due_date: Optional[date] = Field(default=None, description="下次复习日期")

    # 学习统计
    study_count: int = Field(default=0, description="学习次数")
    correct_count: int = Field(default=0, description="正确次数")
    wrong_count: int = Field(default=0, description="错误次数")
    last_studied: Optional[datetime] = Field(default=None, description="最后学习时间")
    first_seen: Optional[datetime] = Field(default=None, description="首次学习时间")

    # 记忆数据
    memory_strength: float = Field(default=0.0, ge=0.0, le=1.0, description="记忆强度")

    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"onupdate": datetime.utcnow},
        description="更新时间"
    )

    # 关系
    user_rel: "User" = Relationship(back_populates="word_progress_rel")
    word_rel: "Word" = Relationship(back_populates="word_progress_rel")
    learning_plan_rel: "UserLearningPlan" = Relationship(back_populates="word_progress_rel")

    # Pydantic验证器
    @field_validator('familiarity')
    @classmethod
    def validate_familiarity(cls, v: int) -> int:
        """验证熟悉程度范围"""
        if not 0 <= v <= 100:
            raise ValueError('熟悉程度必须在0-100之间')
        return v

    @field_validator('ease_factor')
    @classmethod
    def validate_ease_factor(cls, v: float) -> float:
        """验证简易因子范围"""
        if not 1.3 <= v <= 3.0:
            raise ValueError('简易因子必须在1.3-3.0之间')
        return round(v, 2)

    @field_validator('memory_strength')
    @classmethod
    def validate_memory_strength(cls, v: float) -> float:
        """验证记忆强度范围"""
        if not 0.0 <= v <= 1.0:
            raise ValueError('记忆强度必须在0.0-1.0之间')
        return round(v, 2)

    # 计算方法
    def calculate_accuracy_rate(self) -> float:
        """计算正确率"""
        total_attempts = self.correct_count + self.wrong_count
        if total_attempts == 0:
            return 0.0
        return round(self.correct_count / total_attempts, 2)

    def update_status(self) -> None:
        """根据熟悉程度更新学习状态"""
        if self.familiarity >= 80:
            self.status = LearningStatus.MASTERED
        elif self.familiarity >= 50:
            self.status = LearningStatus.REVIEWING
        elif self.familiarity > 0:
            self.status = LearningStatus.LEARNING
        else:
            self.status = LearningStatus.NEW

    def calculate_memory_strength(self) -> float:
        """计算记忆强度"""
        total_studies = self.study_count
        accuracy = self.calculate_accuracy_rate()

        # 简单的记忆强度计算公式
        if total_studies == 0:
            self.memory_strength = 0.0
        else:
            # 基于学习次数和正确率的记忆强度
            self.memory_strength = round(min(1.0, (total_studies * 0.1 + accuracy * 0.5)), 2)

        return self.memory_strength


class UserLearningSetting(SQLModel, table=True):
    """用户学习设置表"""
    __tablename__ = "user_learning_settings"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", unique=True, description="用户ID")

    # 学习目标
    daily_new_goal: int = Field(default=20, ge=1, le=100, description="每日新学目标")
    daily_review_goal: int = Field(default=30, ge=1, le=200, description="每日复习目标")
    weekly_goal: int = Field(default=100, ge=1, le=500, description="每周学习目标")

    # 学习偏好
    default_study_mode: StudyMode = Field(default=StudyMode.WORD_TO_DEFINITION, description="默认学习模式")
    auto_play_sound: bool = Field(default=True, description="自动播放发音")
    show_examples: bool = Field(default=True, description="显示例句")
    show_definitions: bool = Field(default=True, description="显示释义")
    show_phonetics: bool = Field(default=True, description="显示音标")

    # 复习设置
    enable_spaced_repetition: bool = Field(default=True, description="启用间隔重复")
    review_algorithm: str = Field(default="sm2", description="复习算法")
    max_reviews_per_day: int = Field(default=100, ge=10, le=500, description="每日最大复习数")

    # 通知设置
    study_reminder: bool = Field(default=True, description="学习提醒")
    reminder_time: Optional[time] = Field(default=None, description="提醒时间")
    push_notifications: bool = Field(default=True, description="推送通知")

    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"onupdate": datetime.utcnow},
        description="更新时间"
    )

    # 关系
    user_rel: "User" = Relationship(back_populates="learning_setting_rel")

    # Pydantic验证器
    @field_validator('daily_new_goal', 'daily_review_goal')
    @classmethod
    def validate_daily_goals(cls, v: int) -> int:
        """验证每日目标范围"""
        if v < 1:
            raise ValueError('每日目标必须至少为1')
        return v

    @field_validator('weekly_goal')
    @classmethod
    def validate_weekly_goal(cls, v: int) -> int:
        """验证每周目标范围"""
        if v < 7:  # 至少每天1个单词
            raise ValueError('每周目标必须至少为7')
        return v

    @field_validator('max_reviews_per_day')
    @classmethod
    def validate_max_reviews(cls, v: int) -> int:
        """验证最大复习数"""
        if v < 10:
            raise ValueError('每日最大复习数必须至少为10')
        return v


class UserStudyStatistics(SQLModel, table=True):
    """用户学习统计表"""
    __tablename__ = "user_study_statistics"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True, description="用户ID")
    stat_date: date = Field(default_factory=date.today, index=True, description="统计日期")

    # 学习数据
    new_words_studied: int = Field(default=0, description="新学单词数")
    words_reviewed: int = Field(default=0, description="复习单词数")
    total_study_time: int = Field(default=0, description="总学习时长(分钟)")
    sessions_completed: int = Field(default=0, description="完成会话数")

    # 正确率统计
    correct_answers: int = Field(default=0, description="正确回答数")
    total_answers: int = Field(default=0, description="总回答数")
    accuracy_rate: float = Field(default=0.0, ge=0.0, le=1.0, description="正确率")

    # 回答类型统计
    known_answers: int = Field(default=0, description="认识次数")
    unknown_answers: int = Field(default=0, description="不认识次数")
    uncertain_answers: int = Field(default=0, description="模糊次数")

    # 连续学习
    current_streak: int = Field(default=0, description="当前连续学习天数")
    longest_streak: int = Field(default=0, description="最长连续学习天数")

    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"onupdate": datetime.utcnow},
        description="更新时间"
    )

    # 关系
    user_rel: "User" = Relationship(back_populates="study_statistics_rel")

    # Pydantic验证器
    @field_validator('accuracy_rate')
    @classmethod
    def validate_accuracy_rate(cls, v: float) -> float:
        """验证正确率范围"""
        if not 0.0 <= v <= 1.0:
            raise ValueError('正确率必须在0.0到1.0之间')
        return round(v, 2)

    @field_validator('stat_date')
    @classmethod
    def validate_stat_date(cls, v: date) -> date:
        """验证统计日期不能是未来日期"""
        if v > date.today():
            raise ValueError('统计日期不能是未来日期')
        return v

    # 计算方法
    def calculate_accuracy(self) -> float:
        """计算正确率"""
        if self.total_answers > 0:
            self.accuracy_rate = round(self.correct_answers / self.total_answers, 2)
        else:
            self.accuracy_rate = 0.0
        return self.accuracy_rate

    def calculate_total_words(self) -> int:
        """计算总学习单词数"""
        return self.new_words_studied + self.words_reviewed

    def calculate_study_efficiency(self) -> float:
        """计算学习效率（单词/分钟）"""
        if self.total_study_time == 0:
            return 0.0
        total_words = self.calculate_total_words()
        return round(total_words / self.total_study_time, 2)

    def calculate_answer_distribution(self) -> dict:
        """计算回答类型分布"""
        total_answers = self.known_answers + self.unknown_answers + self.uncertain_answers
        if total_answers == 0:
            return {"known": 0.0, "unknown": 0.0, "uncertain": 0.0}

        return {
            "known": round(self.known_answers / total_answers, 2),
            "unknown": round(self.unknown_answers / total_answers, 2),
            "uncertain": round(self.uncertain_answers / total_answers, 2)
        }
