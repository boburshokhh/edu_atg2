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


class FinalTest(models.Model):
    id = models.AutoField(primary_key=True)
    course_program = models.ForeignKey(
        CourseProgram, db_column="course_program_id", on_delete=models.CASCADE
    )
    title = models.CharField(max_length=500)
    questions_count = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "final_tests"
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








