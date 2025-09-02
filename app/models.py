from sqlmodel import SQLModel, Field, Relationship, JSON, Column
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from decimal import Decimal


# Enums for better type safety
class StudentGrade(str, Enum):
    GRADE_4 = "4"
    GRADE_5 = "5"
    GRADE_6 = "6"


class QuestionDifficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class QuestionType(str, Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"
    SHORT_ANSWER = "short_answer"


class BadgeType(str, Enum):
    LEVEL_COMPLETION = "level_completion"
    STREAK = "streak"
    PERFECT_SCORE = "perfect_score"
    EXPLORER = "explorer"
    SCHOLAR = "scholar"


class MediaType(str, Enum):
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    DOCUMENT = "document"
    MODEL_3D = "model_3d"


class ARTriggerType(str, Enum):
    BANKNOTE = "banknote"
    STAMP = "stamp"
    TEXTBOOK_IMAGE = "textbook_image"
    QR_CODE = "qr_code"


# Base User Management
class User(SQLModel, table=True):
    __tablename__ = "users"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(max_length=50, unique=True, index=True)
    email: str = Field(max_length=255, unique=True, index=True)
    full_name: str = Field(max_length=100)
    is_teacher: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    student_profile: Optional["StudentProfile"] = Relationship(back_populates="user")
    teacher_profile: Optional["TeacherProfile"] = Relationship(back_populates="user")


class StudentProfile(SQLModel, table=True):
    __tablename__ = "student_profiles"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", unique=True)
    grade: StudentGrade
    school_name: str = Field(max_length=200)
    total_points: int = Field(default=0)
    current_level: int = Field(default=1)
    streak_days: int = Field(default=0)
    last_activity: Optional[datetime] = None

    # Relationships
    user: User = Relationship(back_populates="student_profile")
    quiz_attempts: List["QuizAttempt"] = Relationship(back_populates="student")
    student_badges: List["StudentBadge"] = Relationship(back_populates="student")
    hero_diary_progress: List["HeroDiaryProgress"] = Relationship(back_populates="student")


class TeacherProfile(SQLModel, table=True):
    __tablename__ = "teacher_profiles"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", unique=True)
    school_name: str = Field(max_length=200)
    certification_number: Optional[str] = Field(max_length=50)
    specialization: Optional[str] = Field(max_length=100)

    # Relationships
    user: User = Relationship(back_populates="teacher_profile")
    lesson_plans: List["LessonPlan"] = Relationship(back_populates="created_by")


# 1. Learning Modules (Modul Pembelajaran)
class LessonPlan(SQLModel, table=True):
    __tablename__ = "lesson_plans"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=200)
    description: str = Field(max_length=1000)
    grade_level: StudentGrade
    subject: str = Field(max_length=100)
    duration_minutes: int = Field(gt=0)
    learning_objectives: List[str] = Field(default=[], sa_column=Column(JSON))
    curriculum_alignment: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    gamification_elements: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    created_by_id: int = Field(foreign_key="teacher_profiles.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_validated: bool = Field(default=False)

    # Relationships
    created_by: TeacherProfile = Relationship(back_populates="lesson_plans")
    teaching_materials: List["TeachingMaterial"] = Relationship(back_populates="lesson_plan")
    activity_sheets: List["ActivitySheet"] = Relationship(back_populates="lesson_plan")


class TeachingMaterial(SQLModel, table=True):
    __tablename__ = "teaching_materials"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    lesson_plan_id: int = Field(foreign_key="lesson_plans.id")
    title: str = Field(max_length=200)
    material_type: MediaType
    file_path: str = Field(max_length=500)
    description: Optional[str] = Field(max_length=500)
    display_order: int = Field(default=0)
    is_validated: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    lesson_plan: LessonPlan = Relationship(back_populates="teaching_materials")


class ActivitySheet(SQLModel, table=True):
    __tablename__ = "activity_sheets"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    lesson_plan_id: int = Field(foreign_key="lesson_plans.id")
    title: str = Field(max_length=200)
    instructions: str = Field(max_length=2000)
    activity_type: str = Field(max_length=50)  # collaborative, exploratory, individual
    estimated_time_minutes: int = Field(gt=0)
    materials_needed: List[str] = Field(default=[], sa_column=Column(JSON))
    assessment_criteria: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    file_path: Optional[str] = Field(max_length=500)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    lesson_plan: LessonPlan = Relationship(back_populates="activity_sheets")


# 2. Quiz Adventure
class HistoricalPeriod(SQLModel, table=True):
    __tablename__ = "historical_periods"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100, unique=True)
    description: str = Field(max_length=1000)
    start_year: Optional[int] = None
    end_year: Optional[int] = None
    display_order: int = Field(default=0)
    background_image: Optional[str] = Field(max_length=500)

    # Relationships
    quiz_levels: List["QuizLevel"] = Relationship(back_populates="historical_period")
    vocabulary_terms: List["VocabularyTerm"] = Relationship(back_populates="historical_period")
    historical_figures: List["HistoricalFigure"] = Relationship(back_populates="historical_period")


class QuizLevel(SQLModel, table=True):
    __tablename__ = "quiz_levels"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    historical_period_id: int = Field(foreign_key="historical_periods.id")
    level_number: int = Field(gt=0)
    title: str = Field(max_length=200)
    description: str = Field(max_length=500)
    unlock_points_required: int = Field(default=0)
    completion_points_reward: int = Field(gt=0)
    max_attempts: Optional[int] = Field(default=3)
    time_limit_minutes: Optional[int] = None

    # Relationships
    historical_period: HistoricalPeriod = Relationship(back_populates="quiz_levels")
    questions: List["QuizQuestion"] = Relationship(back_populates="quiz_level")
    quiz_attempts: List["QuizAttempt"] = Relationship(back_populates="quiz_level")


class QuizQuestion(SQLModel, table=True):
    __tablename__ = "quiz_questions"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    quiz_level_id: int = Field(foreign_key="quiz_levels.id")
    question_text: str = Field(max_length=1000)
    question_type: QuestionType
    difficulty: QuestionDifficulty
    points_value: int = Field(gt=0, default=10)
    explanation: str = Field(max_length=1000)
    media_url: Optional[str] = Field(max_length=500)
    correct_answer: str = Field(max_length=500)
    answer_options: Optional[List[str]] = Field(default=[], sa_column=Column(JSON))
    display_order: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    quiz_level: QuizLevel = Relationship(back_populates="questions")
    student_answers: List["StudentAnswer"] = Relationship(back_populates="question")


class QuizAttempt(SQLModel, table=True):
    __tablename__ = "quiz_attempts"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    student_id: int = Field(foreign_key="student_profiles.id")
    quiz_level_id: int = Field(foreign_key="quiz_levels.id")
    attempt_number: int = Field(gt=0)
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    score: Optional[int] = Field(default=0)
    total_points_earned: int = Field(default=0)
    is_completed: bool = Field(default=False)
    is_passed: bool = Field(default=False)

    # Relationships
    student: StudentProfile = Relationship(back_populates="quiz_attempts")
    quiz_level: QuizLevel = Relationship(back_populates="quiz_attempts")
    student_answers: List["StudentAnswer"] = Relationship(back_populates="quiz_attempt")


class StudentAnswer(SQLModel, table=True):
    __tablename__ = "student_answers"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    quiz_attempt_id: int = Field(foreign_key="quiz_attempts.id")
    question_id: int = Field(foreign_key="quiz_questions.id")
    student_answer: str = Field(max_length=1000)
    is_correct: bool
    points_earned: int = Field(default=0)
    answered_at: datetime = Field(default_factory=datetime.utcnow)
    time_taken_seconds: Optional[int] = None

    # Relationships
    quiz_attempt: QuizAttempt = Relationship(back_populates="student_answers")
    question: QuizQuestion = Relationship(back_populates="student_answers")


class Badge(SQLModel, table=True):
    __tablename__ = "badges"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100, unique=True)
    description: str = Field(max_length=500)
    badge_type: BadgeType
    icon_url: str = Field(max_length=500)
    criteria: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    points_reward: int = Field(default=0)
    is_active: bool = Field(default=True)

    # Relationships
    student_badges: List["StudentBadge"] = Relationship(back_populates="badge")


class StudentBadge(SQLModel, table=True):
    __tablename__ = "student_badges"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    student_id: int = Field(foreign_key="student_profiles.id")
    badge_id: int = Field(foreign_key="badges.id")
    earned_at: datetime = Field(default_factory=datetime.utcnow)
    progress_data: Optional[Dict[str, Any]] = Field(default={}, sa_column=Column(JSON))

    # Relationships
    student: StudentProfile = Relationship(back_populates="student_badges")
    badge: Badge = Relationship(back_populates="student_badges")


# 3. Vocab Explorer
class VocabularyTerm(SQLModel, table=True):
    __tablename__ = "vocabulary_terms"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    historical_period_id: Optional[int] = Field(foreign_key="historical_periods.id")
    term: str = Field(max_length=100, index=True)
    definition: str = Field(max_length=2000)
    pronunciation: Optional[str] = Field(max_length=200)
    audio_url: Optional[str] = Field(max_length=500)
    etymology: Optional[str] = Field(max_length=500)
    usage_example: Optional[str] = Field(max_length=1000)
    difficulty_level: QuestionDifficulty
    grade_level: StudentGrade
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    historical_period: Optional[HistoricalPeriod] = Relationship(back_populates="vocabulary_terms")
    visual_content: List["VocabularyVisual"] = Relationship(back_populates="vocabulary_term")
    term_connections: List["TermConnection"] = Relationship(
        back_populates="source_term", sa_relationship_kwargs={"foreign_keys": "TermConnection.source_term_id"}
    )
    connected_from: List["TermConnection"] = Relationship(
        back_populates="target_term", sa_relationship_kwargs={"foreign_keys": "TermConnection.target_term_id"}
    )


class VocabularyVisual(SQLModel, table=True):
    __tablename__ = "vocabulary_visuals"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    vocabulary_term_id: int = Field(foreign_key="vocabulary_terms.id")
    media_type: MediaType
    media_url: str = Field(max_length=500)
    caption: Optional[str] = Field(max_length=500)
    alt_text: str = Field(max_length=300)
    display_order: int = Field(default=0)

    # Relationships
    vocabulary_term: VocabularyTerm = Relationship(back_populates="visual_content")


class TermConnection(SQLModel, table=True):
    __tablename__ = "term_connections"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    source_term_id: int = Field(foreign_key="vocabulary_terms.id")
    target_term_id: int = Field(foreign_key="vocabulary_terms.id")
    relationship_type: str = Field(max_length=50)  # synonym, antonym, related_to, part_of
    description: Optional[str] = Field(max_length=500)
    strength: int = Field(default=1, ge=1, le=5)  # Connection strength 1-5

    # Relationships
    source_term: VocabularyTerm = Relationship(
        back_populates="term_connections", sa_relationship_kwargs={"foreign_keys": "TermConnection.source_term_id"}
    )
    target_term: VocabularyTerm = Relationship(
        back_populates="connected_from", sa_relationship_kwargs={"foreign_keys": "TermConnection.target_term_id"}
    )


# 4. Hero's Diary
class HistoricalFigure(SQLModel, table=True):
    __tablename__ = "historical_figures"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    historical_period_id: Optional[int] = Field(foreign_key="historical_periods.id")
    name: str = Field(max_length=100, index=True)
    birth_year: Optional[int] = None
    death_year: Optional[int] = None
    birth_place: Optional[str] = Field(max_length=200)
    occupation: Optional[str] = Field(max_length=100)
    biography_summary: str = Field(max_length=2000)
    major_contributions: List[str] = Field(default=[], sa_column=Column(JSON))
    famous_quotes: List[str] = Field(default=[], sa_column=Column(JSON))
    portrait_url: Optional[str] = Field(max_length=500)
    is_featured: bool = Field(default=False)
    reading_level: StudentGrade
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    historical_period: Optional[HistoricalPeriod] = Relationship(back_populates="historical_figures")
    diary_entries: List["DiaryEntry"] = Relationship(back_populates="historical_figure")
    timeline_events: List["TimelineEvent"] = Relationship(back_populates="historical_figure")
    multimedia_content: List["FigureMultimedia"] = Relationship(back_populates="historical_figure")
    hero_diary_progress: List["HeroDiaryProgress"] = Relationship(back_populates="historical_figure")
    ar_models: List["ARModel"] = Relationship(back_populates="historical_figure")


class DiaryEntry(SQLModel, table=True):
    __tablename__ = "diary_entries"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    historical_figure_id: int = Field(foreign_key="historical_figures.id")
    title: str = Field(max_length=200)
    entry_text: str = Field(max_length=5000)
    entry_date: Optional[datetime] = None  # Historical date (if known)
    historical_context: str = Field(max_length=1000)
    emotional_tone: Optional[str] = Field(max_length=50)
    display_order: int = Field(default=0)
    is_fictional: bool = Field(default=True)  # Most entries will be interpretive
    sources: Optional[List[str]] = Field(default=[], sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    historical_figure: HistoricalFigure = Relationship(back_populates="diary_entries")


class TimelineEvent(SQLModel, table=True):
    __tablename__ = "timeline_events"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    historical_figure_id: int = Field(foreign_key="historical_figures.id")
    title: str = Field(max_length=200)
    description: str = Field(max_length=1000)
    event_date: Optional[datetime] = None
    event_year: Optional[int] = None  # For cases where only year is known
    importance_level: int = Field(default=1, ge=1, le=5)
    location: Optional[str] = Field(max_length=200)
    display_order: int = Field(default=0)

    # Relationships
    historical_figure: HistoricalFigure = Relationship(back_populates="timeline_events")


class FigureMultimedia(SQLModel, table=True):
    __tablename__ = "figure_multimedia"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    historical_figure_id: int = Field(foreign_key="historical_figures.id")
    media_type: MediaType
    media_url: str = Field(max_length=500)
    title: str = Field(max_length=200)
    description: Optional[str] = Field(max_length=500)
    source_attribution: Optional[str] = Field(max_length=300)
    display_order: int = Field(default=0)
    is_primary: bool = Field(default=False)

    # Relationships
    historical_figure: HistoricalFigure = Relationship(back_populates="multimedia_content")


class HeroDiaryProgress(SQLModel, table=True):
    __tablename__ = "hero_diary_progress"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    student_id: int = Field(foreign_key="student_profiles.id")
    historical_figure_id: int = Field(foreign_key="historical_figures.id")
    entries_read: int = Field(default=0)
    total_entries: int = Field(default=0)
    completion_percentage: Decimal = Field(default=Decimal("0"), max_digits=5, decimal_places=2)
    last_accessed: datetime = Field(default_factory=datetime.utcnow)
    favorite_entries: List[int] = Field(default=[], sa_column=Column(JSON))
    notes: Optional[str] = Field(max_length=2000)

    # Relationships
    student: StudentProfile = Relationship(back_populates="hero_diary_progress")
    historical_figure: HistoricalFigure = Relationship(back_populates="hero_diary_progress")


# 5. Augmented Reality (AR)
class ARTrigger(SQLModel, table=True):
    __tablename__ = "ar_triggers"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    trigger_type: ARTriggerType
    trigger_name: str = Field(max_length=100)
    description: str = Field(max_length=500)
    recognition_data: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))  # Image features, QR data, etc.
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    ar_experiences: List["ARExperience"] = Relationship(back_populates="ar_trigger")


class ARModel(SQLModel, table=True):
    __tablename__ = "ar_models"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    historical_figure_id: Optional[int] = Field(foreign_key="historical_figures.id")
    model_name: str = Field(max_length=100)
    model_file_path: str = Field(max_length=500)
    texture_file_path: Optional[str] = Field(max_length=500)
    animation_file_path: Optional[str] = Field(max_length=500)
    scale_factor: Decimal = Field(default=Decimal("1.0"), max_digits=5, decimal_places=3)
    animation_triggers: List[str] = Field(default=[], sa_column=Column(JSON))
    interaction_points: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    file_size_mb: Optional[Decimal] = Field(max_digits=8, decimal_places=2)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    historical_figure: Optional[HistoricalFigure] = Relationship(back_populates="ar_models")
    ar_experiences: List["ARExperience"] = Relationship(back_populates="ar_model")


class ARExperience(SQLModel, table=True):
    __tablename__ = "ar_experiences"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    ar_trigger_id: int = Field(foreign_key="ar_triggers.id")
    ar_model_id: int = Field(foreign_key="ar_models.id")
    experience_name: str = Field(max_length=100)
    description: str = Field(max_length=500)
    interactive_elements: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    storytelling_content: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    audio_narration_url: Optional[str] = Field(max_length=500)
    duration_seconds: Optional[int] = None
    grade_level: StudentGrade
    is_active: bool = Field(default=True)

    # Relationships
    ar_trigger: ARTrigger = Relationship(back_populates="ar_experiences")
    ar_model: ARModel = Relationship(back_populates="ar_experiences")
    ar_sessions: List["ARSession"] = Relationship(back_populates="ar_experience")


class ARSession(SQLModel, table=True):
    __tablename__ = "ar_sessions"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    student_id: Optional[int] = Field(foreign_key="student_profiles.id")  # Optional for anonymous usage
    ar_experience_id: int = Field(foreign_key="ar_experiences.id")
    session_start: datetime = Field(default_factory=datetime.utcnow)
    session_end: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    interactions_count: int = Field(default=0)
    completion_status: str = Field(default="started")  # started, completed, abandoned
    device_info: Optional[Dict[str, Any]] = Field(default={}, sa_column=Column(JSON))

    # Relationships
    student: Optional[StudentProfile] = Relationship()
    ar_experience: ARExperience = Relationship(back_populates="ar_sessions")


# Non-persistent schemas for validation and API
class UserCreate(SQLModel, table=False):
    username: str = Field(max_length=50)
    email: str = Field(max_length=255)
    full_name: str = Field(max_length=100)
    is_teacher: bool = Field(default=False)


class StudentCreate(SQLModel, table=False):
    grade: StudentGrade
    school_name: str = Field(max_length=200)


class TeacherCreate(SQLModel, table=False):
    school_name: str = Field(max_length=200)
    certification_number: Optional[str] = Field(max_length=50)
    specialization: Optional[str] = Field(max_length=100)


class QuizAttemptCreate(SQLModel, table=False):
    quiz_level_id: int


class StudentAnswerCreate(SQLModel, table=False):
    question_id: int
    student_answer: str = Field(max_length=1000)


class VocabularyTermCreate(SQLModel, table=False):
    historical_period_id: Optional[int] = None
    term: str = Field(max_length=100)
    definition: str = Field(max_length=2000)
    pronunciation: Optional[str] = Field(max_length=200)
    difficulty_level: QuestionDifficulty
    grade_level: StudentGrade


class HeroDiaryProgressUpdate(SQLModel, table=False):
    entries_read: Optional[int] = None
    notes: Optional[str] = Field(max_length=2000)
    favorite_entries: Optional[List[int]] = None


class ARSessionCreate(SQLModel, table=False):
    ar_experience_id: int
    device_info: Optional[Dict[str, Any]] = None
