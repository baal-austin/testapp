# app/crud/study.py
from datetime import timedelta
from typing import Any

from sqlalchemy.orm import Session
from sqlmodel import select, and_, desc, col


from app.schemas.study import *
from app.models.word import Word, WordDefinition, WordPronunciation, Example
from app.models.book import WordbookWordLink, Wordbook

# ===== 学习计划管理 =====
def create_learning_plan_by_id(db: Session, user_id: int, plan_data: LearningPlanCreate) -> UserLearningPlan:
    """创建学习计划"""
    # 检查词库是否存在
    wordbook = db.get(Wordbook, plan_data.wordbook_id)
    if not wordbook:
        raise ValueError("词库不存在")

    # 停用其他活跃计划
    _deactivate_other_plans(db, user_id)

    # 计算词库总单词数
    total_words = _get_wordbook_word_count(db, plan_data.wordbook_id)

    plan = UserLearningPlan(
        user_id=user_id,
        wordbook_id=plan_data.wordbook_id,
        name=plan_data.name,
        daily_new_words=plan_data.daily_new_words,
        daily_review_words=plan_data.daily_review_words,
        total_words=total_words
    )

    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


def get_current_learning_plan(db: Session, user_id: int) -> Optional[UserLearningPlan]:
    """获取当前活跃的学习计划"""
    statement = select(UserLearningPlan).where(
        and_(
            UserLearningPlan.user_id == user_id,
            UserLearningPlan.is_active == True
        )
    )
    result = db.execute(statement)
    return result.scalars().first()


def get_learning_plan(db: Session, user_id: int, plan_id: int) -> Optional[UserLearningPlan]:
    """获取指定学习计划"""
    statement = select(UserLearningPlan).where(
        and_(
            UserLearningPlan.user_id == user_id,
            UserLearningPlan.id == plan_id
        )
    )
    result = db.execute(statement)
    return result.scalars().first()


def get_all_learning_plans(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[UserLearningPlan]:
    """获取用户的所有学习计划"""
    statement = select(UserLearningPlan).where(
        UserLearningPlan.user_id == user_id
    ).order_by(desc(UserLearningPlan.created_at)).offset(skip).limit(limit)
    result = db.execute(statement)
    return result.scalars().all()


def update_learning_plan(db: Session, user_id: int, plan_id: int, plan_data: LearningPlanUpdate) -> \
        Optional[UserLearningPlan]:
    """更新学习计划"""
    plan = get_learning_plan(db, user_id, plan_id)
    if not plan:
        return None

    update_data = plan_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(plan, field, value)

    plan.updated_at = datetime.utcnow()
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


def switch_learning_plan(db: Session, user_id: int, plan_id: int) -> Optional[UserLearningPlan]:
    """切换到指定学习计划"""
    # 停用其他活跃计划
    _deactivate_other_plans(db, user_id)

    # 激活指定计划
    plan = get_learning_plan(db, user_id, plan_id)
    if plan:
        plan.is_active = True
        plan.updated_at = datetime.utcnow()
        db.add(plan)
        db.commit()
        db.refresh(plan)

    return plan


def delete_learning_plan(db: Session, user_id: int, plan_id: int) -> bool:
    """删除学习计划"""
    plan = get_learning_plan(db, user_id, plan_id)
    if not plan:
        return False

    if plan.is_active:
        raise ValueError("不能删除活跃的学习计划")

    db.delete(plan)
    db.commit()
    return True


def _deactivate_other_plans(db: Session, user_id: int):
    """停用用户的其他活跃计划"""
    statement = select(UserLearningPlan).where(
        and_(
            UserLearningPlan.user_id == user_id,
            UserLearningPlan.is_active == True
        )
    )
    result = db.execute(statement)
    active_plans = result.scalars().all()

    for plan in active_plans:
        plan.is_active = False
        plan.updated_at = datetime.utcnow()
        db.add(plan)

    if active_plans:
        db.commit()


def _get_wordbook_word_count(db: Session, wordbook_id: int) -> int:
    """获取词库单词数量"""
    statement = select(WordbookWordLink).where(
        WordbookWordLink.wordbook_id == wordbook_id
    )
    result = db.execute(statement)
    return len(result.scalars().all())


# ===== 每日任务管理 =====
def get_or_create_daily_task(db: Session, user_id: int, task_date: date = None) -> UserDailyTask:
    """获取或创建每日任务"""
    if task_date is None:
        task_date = date.today()

    plan = get_current_learning_plan(db, user_id)
    if not plan:
        raise ValueError("没有激活的学习计划")

    statement = select(UserDailyTask).where(
        and_(
            UserDailyTask.user_id == user_id,
            UserDailyTask.task_date == task_date
        )
    )
    result = db.execute(statement)
    task = result.scalars().first()

    if not task:
        task = UserDailyTask(
            user_id=user_id,
            learning_plan_id=plan.id,
            task_date=task_date,
            target_new_words=plan.daily_new_words,
            target_review_words=plan.daily_review_words
        )
        db.add(task)
        db.commit()
        db.refresh(task)

    return task


def get_daily_task(db: Session, user_id: int, task_date: date) -> Optional[UserDailyTask]:
    """获取指定日期的任务"""
    statement = select(UserDailyTask).where(
        and_(
            UserDailyTask.user_id == user_id,
            UserDailyTask.task_date == task_date
        )
    )
    result = db.execute(statement)
    return result.scalars().first()


def get_recent_daily_tasks_by_id(db: Session, user_id: int, days: int = 7) -> List[UserDailyTask]:
    """获取最近几天的任务"""
    start_date = date.today() - timedelta(days=days - 1)

    statement = select(UserDailyTask).where(
        and_(
            UserDailyTask.user_id == user_id,
            UserDailyTask.task_date >= start_date,
            UserDailyTask.task_date <= date.today()
        )
    ).order_by(desc(UserDailyTask.task_date))

    result = db.execute(statement)
    return result.scalars().all()


# ===== 学习单词管理 =====
def get_today_study_words(db: Session, user_id: int) -> Dict[str, Any]:
    """获取今日需要学习的单词"""
    task = get_or_create_daily_task(db, user_id)
    plan = task.learning_plan_rel

    # 获取词库中的所有单词
    wordbook_words = _get_wordbook_words(db, plan.wordbook_id)

    # 获取用户的学习进度
    user_progress = _get_user_word_progress(db, user_id, plan.id)

    # 分类单词
    new_words = []
    review_words = []

    for word in wordbook_words:
        progress = user_progress.get(word.id)

        if not progress or progress.status == LearningStatus.NEW:
            # 新单词
            new_words.append(_format_word_data(db, word))
        elif (progress.status in [LearningStatus.LEARNING, LearningStatus.REVIEWING] and
              progress.due_date and progress.due_date <= date.today()):
            # 需要复习的单词
            review_words.append(_format_word_data(db, word, progress))

    # 限制数量
    remaining_new = max(0, task.target_new_words - task.completed_new_words)
    remaining_review = max(0, task.target_review_words - task.completed_reviews)

    return {
        "new_words": new_words[:remaining_new],
        "review_words": review_words[:remaining_review],
        "remaining_new": remaining_new,
        "remaining_review": remaining_review
    }


def get_more_words_to_study(db: Session, user_id: int, count: int = 10) -> List[Dict[str, Any]]:
    """获取更多可学习的单词"""
    plan = get_current_learning_plan(db, user_id)
    if not plan:
        return []

    wordbook_words = _get_wordbook_words(db, plan.wordbook_id)
    user_progress = _get_user_word_progress(db, user_id, plan.id)

    # 获取未学过的单词
    new_words = []
    for word in wordbook_words:
        if word.id not in user_progress:
            new_words.append(_format_word_data(db, word))
            if len(new_words) >= count:
                break

    return new_words


def get_review_words(db: Session, user_id: int, due_before: date, limit: int = 50) -> List[Dict[str, Any]]:
    """获取需要复习的单词"""
    plan = get_current_learning_plan(db, user_id)
    if not plan:
        return []

    # 修复方法1：使用 col() 函数
    statement = select(UserWordProgress).where(
        and_(
            UserWordProgress.user_id == user_id,
            UserWordProgress.learning_plan_id == plan.id,
            UserWordProgress.due_date <= due_before,
            col(UserWordProgress.status).in_([LearningStatus.LEARNING, LearningStatus.REVIEWING])
        )
    ).limit(limit)

    result = db.execute(statement)
    progress_list = result.scalars().all()

    words = []
    for progress in progress_list:
        word_data = _format_word_data(db, progress.word_rel, progress)
        words.append(word_data)

    return words


def get_word_progress(
        db: Session,
        user_id: int,
        status: Optional[LearningStatus] = None,
        min_familiarity: int = 0,
        max_familiarity: int = 100,
        limit: int = 100
) -> List[UserWordProgress]:
    """获取单词学习进度"""
    plan = get_current_learning_plan(db, user_id)
    if not plan:
        return []

    # 构建查询条件
    conditions = [
        UserWordProgress.user_id == user_id,
        UserWordProgress.learning_plan_id == plan.id,
        UserWordProgress.familiarity >= min_familiarity,
        UserWordProgress.familiarity <= max_familiarity
    ]

    if status:
        conditions.append(UserWordProgress.status == status)

    statement = select(UserWordProgress).where(
        and_(*conditions)
    ).order_by(desc(UserWordProgress.updated_at)).limit(limit)

    result = db.execute(statement)
    return result.scalars().all()


def _get_wordbook_words(db: Session, wordbook_id: int) -> List[Word]:
    """获取词库中的所有单词"""
    statement = select(Word).join(
        WordbookWordLink, Word.id == WordbookWordLink.word_id
    ).where(WordbookWordLink.wordbook_id == wordbook_id)

    result = db.execute(statement)
    return result.scalars().all()


def _get_user_word_progress(db: Session, user_id: int, learning_plan_id: int) -> Dict[int, UserWordProgress]:
    """获取用户单词进度字典"""
    statement = select(UserWordProgress).where(
        and_(
            UserWordProgress.user_id == user_id,
            UserWordProgress.learning_plan_id == learning_plan_id
        )
    )
    result = db.execute(statement)
    progress_list = result.scalars().all()
    return {p.word_id: p for p in progress_list}


def _format_word_data(db: Session, word: Word, progress: Optional[UserWordProgress] = None) -> Dict[str, Any]:
    """格式化单词数据"""
    # 获取单词的详细信息
    definitions = db.execute(
        select(WordDefinition.definition).where(WordDefinition.word_id == word.id)
    ).scalars().all()

    examples = db.execute(
        select(Example.example).where(Example.word_id == word.id)
    ).scalars().all()

    pronunciations = db.execute(
        select(WordPronunciation.pronunciation).where(WordPronunciation.word_id == word.id)
    ).scalars().all()

    word_data = {
        "id": word.id,
        "word": word.word,
        "normalized_word": word.normalized_word,
        "definitions": definitions,
        "examples": examples,
        "pronunciations": pronunciations
    }

    if progress:
        word_data.update({
            "status": progress.status,
            "familiarity": progress.familiarity,
            "study_count": progress.study_count,
            "accuracy_rate": progress.calculate_accuracy_rate(),
            "due_date": progress.due_date,
            "memory_strength": progress.memory_strength
        })

    return word_data


# ===== 学习会话管理 =====
def start_study_session(db: Session, user_id: int, session_data: StudySessionCreate) -> UserStudySession:
    """开始学习会话"""
    task = get_or_create_daily_task(db, user_id)

    session = UserStudySession(
        user_id=user_id,
        learning_plan_id=task.learning_plan_id,
        daily_task_id=task.id,
        session_type=session_data.session_type,
        study_mode=session_data.study_mode,
        start_time=datetime.utcnow()
    )

    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def end_study_session(db: Session, user_id: int, session_id: int) -> Optional[UserStudySession]:
    """结束学习会话"""
    session = _get_study_session(db, user_id, session_id)
    if not session:
        return None

    session.end_session()
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def get_study_session(db: Session, user_id: int, session_id: int) -> Optional[UserStudySession]:
    """获取学习会话"""
    statement = select(UserStudySession).where(
        and_(
            UserStudySession.user_id == user_id,
            UserStudySession.id == session_id
        )
    )
    result = db.execute(statement)
    return result.scalars().first()


def get_recent_study_sessions(db: Session, user_id: int, days: int = 7, limit: int = 50) -> List[UserStudySession]:
    """获取最近的学习会话"""
    start_date = datetime.utcnow() - timedelta(days=days)

    statement = select(UserStudySession).where(
        and_(
            UserStudySession.user_id == user_id,
            UserStudySession.start_time >= start_date
        )
    ).order_by(desc(UserStudySession.start_time)).limit(limit)

    result = db.execute(statement)
    return result.scalars().all()


def _get_study_session(db: Session, user_id: int, session_id: int) -> Optional[UserStudySession]:
    """获取学习会话（内部使用）"""
    return get_study_session(db, user_id, session_id)


# ===== 学习记录管理 =====
def record_word_study(db: Session, user_id: int, record_data: StudyRecordCreate) -> UserStudyRecord:
    """记录单词学习"""
    # 验证会话是否存在
    session = get_study_session(db, user_id, record_data.study_session_id)
    if not session:
        raise ValueError("学习会话不存在")

    task = get_or_create_daily_task(db, user_id)
    plan = get_current_learning_plan(db, user_id)

    # 判断答案是否正确
    is_correct = _check_answer_correctness(
        record_data.user_answer,
        record_data.correct_answer,
        record_data.answer_type
    )

    # 创建学习记录
    record = UserStudyRecord(
        user_id=user_id,
        word_id=record_data.word_id,
        study_session_id=record_data.study_session_id,
        daily_task_id=task.id,
        learning_plan_id=plan.id if plan else None,
        study_mode=record_data.study_mode,
        answer_type=record_data.answer_type,
        is_correct=is_correct,
        response_time=record_data.response_time,
        question=record_data.question,
        user_answer=record_data.user_answer,
        correct_answer=record_data.correct_answer
    )

    # 更新单词进度
    if plan:
        _update_word_progress(db, user_id, record_data.word_id, plan.id, record_data.answer_type, is_correct)

    # 更新会话统计
    _update_session_stats(db, session, is_correct)

    # 更新任务进度
    _update_daily_task_progress(db, task, session.session_type)

    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_study_records(
        db: Session,
        user_id: int,
        session_id: Optional[int] = None,
        word_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 100
) -> List[UserStudyRecord]:
    """获取学习记录"""
    conditions = [UserStudyRecord.user_id == user_id]

    if session_id:
        conditions.append(UserStudyRecord.study_session_id == session_id)

    if word_id:
        conditions.append(UserStudyRecord.word_id == word_id)

    if start_date:
        conditions.append(UserStudyRecord.created_at >= start_date)

    if end_date:
        conditions.append(UserStudyRecord.created_at <= end_date)

    statement = select(UserStudyRecord).where(
        and_(*conditions)
    ).order_by(desc(UserStudyRecord.created_at)).limit(limit)

    result = db.execute(statement)
    return result.scalars().all()


def _check_answer_correctness(user_answer: str, correct_answer: str, answer_type: AnswerType) -> bool:
    """检查答案是否正确"""
    if answer_type == AnswerType.KNOWN:
        return True
    elif answer_type == AnswerType.UNKNOWN:
        return False
    else:  # UNCERTAIN
        # 对于模糊回答，如果用户答案正确则算正确
        return user_answer and user_answer.lower().strip() == correct_answer.lower().strip()


def _update_word_progress(db: Session, user_id: int, word_id: int, learning_plan_id: int, answer_type: AnswerType,
                          is_correct: bool):
    """更新单词学习进度"""
    # 查找或创建进度记录
    statement = select(UserWordProgress).where(
        and_(
            UserWordProgress.user_id == user_id,
            UserWordProgress.word_id == word_id,
            UserWordProgress.learning_plan_id == learning_plan_id
        )
    )
    result = db.execute(statement)
    progress = result.scalars().first()

    if not progress:
        progress = UserWordProgress(
            user_id=user_id,
            word_id=word_id,
            learning_plan_id=learning_plan_id,
            status=LearningStatus.NEW,
            first_seen=datetime.utcnow()
        )

    # 更新统计
    progress.study_count += 1
    if is_correct:
        progress.correct_count += 1
    else:
        progress.wrong_count += 1

    progress.last_studied = datetime.utcnow()

    # 根据回答类型更新熟悉度
    if answer_type == AnswerType.KNOWN:
        progress.familiarity = min(100, progress.familiarity + 25)
    elif answer_type == AnswerType.UNKNOWN:
        progress.familiarity = max(0, progress.familiarity - 20)
    else:  # UNCERTAIN
        progress.familiarity = max(0, progress.familiarity - 10)

    # 更新状态和计算记忆强度
    progress.update_status()
    progress.calculate_memory_strength()

    # 计算下次复习时间（简单SM-2算法）
    _calculate_next_review(progress, is_correct)

    progress.updated_at = datetime.utcnow()
    db.add(progress)


def _calculate_next_review(progress: UserWordProgress, is_correct: bool):
    """计算下次复习时间"""
    if is_correct:
        if progress.interval == 0:
            progress.interval = 1
        elif progress.interval == 1:
            progress.interval = 3
        else:
            progress.interval = int(progress.interval * progress.ease_factor)
    else:
        progress.interval = 1
        progress.ease_factor = max(1.3, progress.ease_factor - 0.2)

    progress.due_date = date.today() + timedelta(days=progress.interval)


def _update_session_stats(db: Session, session: UserStudySession, is_correct: bool):
    """更新会话统计"""
    session.completed_words += 1
    session.total_words += 1

    if is_correct:
        session.correct_answers += 1
    else:
        session.wrong_answers += 1

    session.calculate_accuracy()
    db.add(session)


def _update_daily_task_progress(db: Session, task: UserDailyTask, session_type: str):
    """更新每日任务进度"""
    if session_type == "new_words":
        task.completed_new_words += 1
    else:
        task.completed_reviews += 1

    # 更新学习时长（简单估算）
    task.study_duration += 1  # 每分钟增加1分钟

    task.check_completion()
    task.updated_at = datetime.utcnow()
    db.add(task)


# ===== 学习历史统计 =====
def get_study_history(db: Session, user_id: int, start_date: date, end_date: date) -> List[Dict[str, Any]]:
    """获取学习历史"""
    days_diff = (end_date - start_date).days + 1
    tasks = get_recent_daily_tasks_by_id(db, user_id, days_diff)

    history = []
    for task in tasks:
        if start_date <= task.task_date <= end_date:
            # 获取当天的学习记录详情
            statement = select(UserStudyRecord).where(
                UserStudyRecord.daily_task_id == task.id
            )
            result = db.execute(statement)
            records = result.scalars().all()

            # 统计各类回答
            known_count = sum(1 for r in records if r.answer_type == AnswerType.KNOWN)
            unknown_count = sum(1 for r in records if r.answer_type == AnswerType.UNKNOWN)
            uncertain_count = sum(1 for r in records if r.answer_type == AnswerType.UNCERTAIN)

            history.append({
                "date": task.task_date,
                "new_words_studied": task.completed_new_words,
                "words_reviewed": task.completed_reviews,
                "study_duration": task.study_duration,
                "accuracy_rate": task.accuracy_rate,
                "known_words": known_count,
                "unknown_words": unknown_count,
                "uncertain_words": uncertain_count,
                "total_words": len(records)
            })

    return history


def get_study_progress(db: Session, user_id: int) -> Dict[str, Any]:
    """获取学习进度概览"""
    plan = get_current_learning_plan(db, user_id)
    today_words = get_today_study_words(db, user_id)

    if not plan:
        return {
            "current_plan": None,
            "wordbook_id": None,
            "today_new_words": 0,
            "today_review_words": 0,
            "daily_goal_new": 0,
            "daily_goal_review": 0,
            "completion_rate": 0.0
        }

    task = get_or_create_daily_task(db, user_id)
    completion_rate = task.calculate_completion_rate()

    return {
        "current_plan": plan.name,
        "wordbook_id": plan.wordbook_id,
        "today_new_words": len(today_words["new_words"]),
        "today_review_words": len(today_words["review_words"]),
        "daily_goal_new": plan.daily_new_words,
        "daily_goal_review": plan.daily_review_words,
        "completion_rate": completion_rate
    }


def get_daily_study_statistics(db: Session, user_id: int, days: int = 7) -> List[UserStudyStatistics]:
    """获取每日学习统计"""
    end_date = date.today()
    start_date = end_date - timedelta(days=days - 1)

    statement = select(UserStudyStatistics).where(
        and_(
            UserStudyStatistics.user_id == user_id,
            UserStudyStatistics.stat_date >= start_date,
            UserStudyStatistics.stat_date <= end_date
        )
    ).order_by(UserStudyStatistics.stat_date)

    result = db.execute(statement)
    return result.scalars().all()


def get_study_statistics_overview(db: Session, user_id: int) -> Dict[str, Any]:
    """获取学习统计概览"""
    # 总学习天数
    statement = select(UserDailyTask).where(
        UserDailyTask.user_id == user_id
    ).distinct(UserDailyTask.task_date)

    result = db.execute(statement)
    total_study_days = len(result.scalars().all())

    # 总学习单词数
    statement = select(UserStudyRecord).where(
        UserStudyRecord.user_id == user_id
    )
    result = db.execute(statement)
    total_study_records = len(result.scalars().all())

    # 总学习时长
    statement = select(UserStudySession).where(
        UserStudySession.user_id == user_id
    )
    result = db.execute(statement)
    sessions = result.scalars().all()
    total_study_duration = sum(session.duration for session in sessions if session.duration)

    # 平均正确率
    statement = select(UserStudyStatistics).where(
        UserStudyStatistics.user_id == user_id
    ).order_by(desc(UserStudyStatistics.stat_date)).limit(30)

    result = db.execute(statement)
    recent_stats = result.scalars().all()

    if recent_stats:
        avg_accuracy = sum(stat.accuracy_rate for stat in recent_stats) / len(recent_stats)
    else:
        avg_accuracy = 0.0

    # 当前计划进度
    plan = get_current_learning_plan(db, user_id)
    if plan:
        mastery_rate = plan.calculate_mastery_rate()
        learning_progress = plan.calculate_learning_progress()
        current_streak = plan.current_streak
    else:
        mastery_rate = 0.0
        learning_progress = 0.0
        current_streak = 0

    return {
        "total_study_days": total_study_days,
        "total_words_studied": total_study_records,
        "total_study_duration": total_study_duration,
        "average_accuracy": round(avg_accuracy, 2),
        "current_streak": current_streak,
        "mastery_rate": mastery_rate,
        "learning_progress": learning_progress
    }


# ===== 学习设置管理 =====
def get_learning_settings(db: Session, user_id: int) -> UserLearningSetting:
    """获取用户学习设置"""
    statement = select(UserLearningSetting).where(
        UserLearningSetting.user_id == user_id
    )
    result = db.execute(statement)
    settings = result.scalars().first()

    if not settings:
        # 创建默认设置
        settings = UserLearningSetting(user_id=user_id)
        db.add(settings)
        db.commit()
        db.refresh(settings)

    return settings


def update_learning_settings(db: Session, user_id: int, settings_data: LearningSettingUpdate) -> UserLearningSetting:
    """更新用户学习设置"""
    settings = get_learning_settings(db, user_id)

    # 更新字段
    update_dict = settings_data.dict(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(settings, field, value)

    settings.updated_at = datetime.utcnow()

    db.add(settings)
    db.commit()
    db.refresh(settings)

    return settings
