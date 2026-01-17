import uuid

from django.db import models


class Course(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    station_id = models.IntegerField(null=True, blank=True)
    duration_hours = models.IntegerField(null=True, blank=True)
    level = models.CharField(max_length=50, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    icon = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "courses"
        managed = False


class CourseProgram(models.Model):
    id = models.AutoField(primary_key=True)
    station_id = models.IntegerField()
    title = models.CharField(max_length=500)
    description = models.TextField(null=True, blank=True)
    duration = models.CharField(max_length=100, null=True, blank=True)
    topics_count = models.IntegerField(default=0)
    lessons_count = models.IntegerField(default=0)
    tests_count = models.IntegerField(default=0)
    format = models.CharField(max_length=50, default="Онлайн")
    is_active = models.BooleanField(default=True)
    order_index = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "course_programs"
        managed = False


class CourseProgramLearningOutcome(models.Model):
    id = models.AutoField(primary_key=True)
    course_program = models.ForeignKey(
        CourseProgram, db_column="course_program_id", on_delete=models.CASCADE
    )
    outcome_text = models.TextField()
    order_index = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "course_program_learning_outcomes"
        managed = False


class CourseProgramRequirement(models.Model):
    id = models.AutoField(primary_key=True)
    course_program = models.ForeignKey(
        CourseProgram, db_column="course_program_id", on_delete=models.CASCADE
    )
    requirement_text = models.TextField()
    order_index = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "course_program_requirements"
        managed = False


class CourseProgramTargetAudience(models.Model):
    id = models.AutoField(primary_key=True)
    course_program = models.ForeignKey(
        CourseProgram, db_column="course_program_id", on_delete=models.CASCADE
    )
    audience_text = models.CharField(max_length=255)
    order_index = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "course_program_target_audience"
        managed = False


class CourseProgramLesson(models.Model):
    id = models.AutoField(primary_key=True)
    course_program = models.ForeignKey(
        CourseProgram, db_column="course_program_id", on_delete=models.CASCADE
    )
    lesson_key = models.TextField()
    title = models.CharField(max_length=500)
    duration = models.CharField(max_length=100, null=True, blank=True)
    order_index = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "course_program_lessons"
        managed = False


class CourseProgramTopic(models.Model):
    id = models.AutoField(primary_key=True)
    lesson = models.ForeignKey(
        CourseProgramLesson, db_column="course_program_lesson_id", on_delete=models.CASCADE
    )
    topic_key = models.TextField()
    code = models.CharField(max_length=50, null=True, blank=True)
    title = models.CharField(max_length=500)
    duration = models.CharField(max_length=50, null=True, blank=True)
    order_index = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "course_program_topics"
        managed = False


class CourseProgramLessonTest(models.Model):
    id = models.AutoField(primary_key=True)
    lesson = models.ForeignKey(
        CourseProgramLesson, db_column="course_program_lesson_id", on_delete=models.CASCADE
    )
    title = models.CharField(max_length=500)
    description = models.TextField(null=True, blank=True)
    questions_count = models.IntegerField(default=0)
    passing_score = models.IntegerField(default=70)
    time_limit = models.IntegerField(default=30)
    attempts = models.IntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "course_program_lesson_tests"
        managed = False


class FinalTest(models.Model):
    id = models.AutoField(primary_key=True)
    course_program = models.ForeignKey(
        CourseProgram, db_column="course_program_id", on_delete=models.CASCADE
    )
    title = models.CharField(max_length=500)
    description = models.TextField(null=True, blank=True)
    questions_count = models.IntegerField(default=0)
    passing_score = models.IntegerField(default=70)
    time_limit = models.IntegerField(default=30)
    attempts = models.IntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "final_tests"
        managed = False


class TestQuestion(models.Model):
    id = models.AutoField(primary_key=True)
    test_id = models.IntegerField()
    test_type = models.CharField(max_length=20)  # 'lesson' or 'final'
    question = models.TextField()
    points = models.IntegerField(default=1)
    image = models.TextField(null=True, blank=True)
    explanation = models.TextField(null=True, blank=True)
    order_index = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "test_questions"
        managed = False


class TestQuestionOption(models.Model):
    id = models.AutoField(primary_key=True)
    question = models.ForeignKey(
        TestQuestion, db_column="question_id", on_delete=models.CASCADE
    )
    option_text = models.TextField()
    is_correct = models.BooleanField(default=False)
    order_index = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "test_question_options"
        managed = False


class TestResult(models.Model):
    id = models.AutoField(primary_key=True)
    test_id = models.IntegerField()
    test_type = models.CharField(max_length=20)  # 'lesson' or 'final'
    user_id = models.UUIDField()
    score = models.IntegerField()
    is_passed = models.BooleanField(default=False)
    correct_answers = models.IntegerField(default=0)
    total_questions = models.IntegerField(default=0)
    time_spent = models.IntegerField(null=True, blank=True)
    answers_data = models.JSONField(null=True, blank=True)
    completed_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "test_results"
        managed = False


class UserCourse(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user_id = models.UUIDField()
    course_id = models.UUIDField()
    progress_percent = models.IntegerField(default=0)
    status = models.CharField(max_length=20, default="not_started")
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    hours_studied = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    last_activity = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "user_courses"
        managed = False


class UserCourseProgram(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user_id = models.UUIDField()
    course_program_id = models.IntegerField()
    progress_percent = models.IntegerField(default=0)
    status = models.CharField(max_length=20, default="not_started")
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    hours_studied = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    last_activity = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "user_course_programs"
        managed = False


class UserCourseMaterial(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user_id = models.UUIDField()
    course_program_id = models.IntegerField()
    material_type = models.CharField(max_length=20)
    material_key = models.TextField()
    is_completed = models.BooleanField(default=False)
    viewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "user_course_materials"
        managed = False


class Certificate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user_id = models.UUIDField()
    course_id = models.UUIDField()
    title = models.CharField(max_length=255)
    issued_at = models.DateTimeField(auto_now_add=True)
    pdf_url = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "certificates"
        managed = False


class CourseComment(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        "accounts.User", db_column="user_id", on_delete=models.CASCADE
    )
    station_id = models.IntegerField(null=True, blank=True)
    lesson_index = models.IntegerField(null=True, blank=True)
    topic_index = models.IntegerField(null=True, blank=True)
    file_object_key = models.TextField(null=True, blank=True)
    comment_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "course_comments"
        managed = False
        ordering = ["-created_at"]


class UserMaterialProgress(models.Model):
    """Tracks user progress in course materials (videos, PDFs) for auto-resume."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user_id = models.UUIDField()
    course_program_id = models.IntegerField()
    lesson_id = models.IntegerField(null=True, blank=True)
    topic_id = models.IntegerField(null=True, blank=True)
    material_key = models.TextField()  # objectKey файла (MinIO key)
    material_type = models.CharField(max_length=20)  # 'video', 'pdf', 'document'

    # Progress tracking
    position_seconds = models.IntegerField(default=0)  # текущая позиция для видео
    duration_seconds = models.IntegerField(null=True, blank=True)  # общая длительность
    progress_percent = models.IntegerField(default=0)  # процент просмотра (0-100)
    is_completed = models.BooleanField(default=False)  # материал полностью просмотрен

    # Timestamps
    last_viewed_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "user_material_progress"
        managed = True  # Django создаст и будет управлять таблицей
        unique_together = [["user_id", "course_program_id", "material_key"]]
        indexes = [
            models.Index(fields=["user_id", "course_program_id"]),
            models.Index(fields=["material_key"]),
        ]








