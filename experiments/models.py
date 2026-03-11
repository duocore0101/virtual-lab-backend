from django.db import models
from django.conf import settings
from django.utils.text import slugify

User = settings.AUTH_USER_MODEL


# =========================================================
# 🔥 STEP 1 – STUDENT APPROVAL EXTENSION (SAFE ADDITION)
# =========================================================
class StudentApproval(models.Model):
    """
    This model extends student approval logic
    without modifying existing User model logic.
    """

    APPROVAL_STATUS = (
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    )

    student = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="student_approval",
        limit_choices_to={"role": "student"}
    )

    selected_teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="pending_students",
        limit_choices_to={"role": "teacher"}
    )

    approval_status = models.CharField(
        max_length=20,
        choices=APPROVAL_STATUS,
        default="pending"
    )

    approved_by_teacher = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Student Approval"
        verbose_name_plural = "Student Approvals"

    def __str__(self):
        return f"{self.student} → {self.approval_status}"


# =========================================================
# EXPERIMENT MASTER
# =========================================================
class Experiment(models.Model):
    EXPERIMENT_TYPES = (
        ('rotarod', 'Rotarod Test'),
        ('maze', 'Maze Test'),
        ('other', 'Other'),
    )

    # -------------------------
    # BASIC INFO
    # -------------------------
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    number = models.IntegerField(default=0)

    # 🔥 SAFE ADDITION (FOR PRACTICAL ORDERING)
    order = models.PositiveIntegerField(
        default=0,
        help_text="Order of experiment in student dashboard"
    )

    experiment_type = models.CharField(
        max_length=50,
        choices=EXPERIMENT_TYPES
    )

    # ✅ SAFE ADDITION (USED IN STUDENT DASHBOARD)
    aim = models.TextField(
        help_text="Aim of the experiment (displayed on student dashboard)"
    )

    description = models.TextField()
    instructions = models.TextField(blank=True)
    
    # -------------------------
    # ASSIGNMENT
    # -------------------------
    teacher = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="assigned_experiments",
        limit_choices_to={"role": "teacher"}
    )


    # -------------------------
    # STATUS & METADATA
    # -------------------------
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    def __str__(self):
        return self.name


# =========================================================
# STUDENT PRACTICAL ATTEMPT
# =========================================================
class ExperimentAttempt(models.Model):
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="experiment_attempts",
        limit_choices_to={"role": "student"}
    )

    experiment = models.ForeignKey(
        Experiment,
        on_delete=models.CASCADE,
        related_name="attempts"
    )

    # 🔥 SAFE ADDITION (ROLL NUMBER SUPPORT)
    roll_no = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="Student roll number (optional)"
    )

    # -------------------------
    # TIMESTAMPS
    # -------------------------
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    # -------------------------
    # PERFORMANCE METRICS (OPTIONAL)
    # -------------------------
    score = models.FloatField(null=True, blank=True)
    remarks = models.TextField(blank=True)

    def __str__(self):
        return f"{self.student} - {self.experiment.name}"


# =========================================================
# OBSERVATIONS (RECORDED VALUES)
# =========================================================
class Observation(models.Model):
    attempt = models.ForeignKey(
        ExperimentAttempt,
        on_delete=models.CASCADE,
        related_name="observations"
    )

    parameter = models.CharField(max_length=100)
    value = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.parameter}: {self.value}"

# =========================================================
# AUDIT LOG (ENTERPRISE FEATURE 🔥)
# =========================================================
class AuditLog(models.Model):
    ACTION_CHOICES = (
        ("create", "Create"),
        ("activate", "Activate"),
        ("deactivate", "Deactivate"),
        ("assign", "Assign"),
        ("login", "Login"),
        ("logout", "Logout"),
    )

    actor = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="audit_actions"
    )

    target_user = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="audit_targets"
    )

    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES
    )

    message = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.actor} → {self.action} → {self.target_user}"
    
# =========================================================
# 🔥 BATCH MANAGEMENT (TEACHER FEATURE)
# =========================================================
class Batch(models.Model):
    """
    Teacher creates batch using roll number range.
    Students automatically mapped dynamically.
    """

    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="batches",
        limit_choices_to={"role": "teacher"}
    )

    name = models.CharField(max_length=100)

    start_roll = models.IntegerField(
        help_text="Starting roll number"
    )

    end_roll = models.IntegerField(
        help_text="Ending roll number"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.start_roll}-{self.end_roll})"


# =========================================================
# 🔥 BATCH ↔ EXPERIMENT ASSIGNMENT
# =========================================================
class BatchExperiment(models.Model):
    """
    Many-to-many relation between Batch and Experiment.
    Defines which practical belongs to which batch.
    """

    batch = models.ForeignKey(
        Batch,
        on_delete=models.CASCADE,
        related_name="assigned_experiments"
    )

    experiment = models.ForeignKey(
        Experiment,
        on_delete=models.CASCADE,
        related_name="batch_assignments"
    )

    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("batch", "experiment")

    def __str__(self):
        return f"{self.batch.name} → {self.experiment.name}"

# =========================================================
# 🔥 EXAM MANAGEMENT SYSTEM (PHASE 1 FOUNDATION)
# =========================================================
class Exam(models.Model):

    EXAM_TYPES = (
        ("internal_1", "Internal Examination Practical Sessional 1st"),
        ("internal_2", "Internal Examination Practical Sessional 2nd"),
        ("external", "External Examination Practical End Semester University Examination"),
    )

    YEAR_CHOICES = (
        ("dpharm_2", "D. Pharm II Year"),
        ("bpharm_4", "B. Pharm II (Semester IV)"),
        ("bpharm_56", "B. Pharm III (Semester V, VI)"),
        ("mpharm_12", "M.Pharm I (Semester I, II)"),
    )

    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="exams",
        limit_choices_to={"role": "teacher"}
    )

    title = models.CharField(max_length=255)

    exam_type = models.CharField(
        max_length=50,
        choices=EXAM_TYPES
    )

    year = models.CharField(
        max_length=50,
        choices=YEAR_CHOICES
    )

    duration_minutes = models.PositiveIntegerField(
        help_text="Duration in minutes (e.g. 120 for 2 hours)"
    )
    viva_marks = models.PositiveIntegerField(
    default=0,
    help_text="Maximum Viva marks for this exam"
    )
    is_active = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} - {self.teacher.first_name}"
    
# =========================================================
# 🔥 MCQ QUESTION BANK (MASTER STORAGE)
# =========================================================
class MCQBank(models.Model):

    question_text = models.TextField()

    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)

    correct_option = models.CharField(
        max_length=1,
        choices=(
            ("A", "Option A"),
            ("B", "Option B"),
            ("C", "Option C"),
            ("D", "Option D"),
        )
    )

    topic = models.CharField(
        max_length=100,
        blank=True,
        help_text="Optional topic/category"
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question_text[:50]
    
# =========================================================
# 🔥 SHORT ANSWER BANK (MASTER STORAGE)
# =========================================================
class ShortAnswerBank(models.Model):

    question_text = models.TextField()

    model_answer = models.TextField(
        blank=True,
        help_text="Optional model answer for teacher reference"
    )

    topic = models.CharField(
        max_length=100,
        blank=True
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question_text[:50]   
    
# =========================================================
# 🔥 EXAM MCQ (ATTACHED TO SPECIFIC EXAM)
# =========================================================
class ExamMCQ(models.Model):

    SOURCE_TYPES = (
        ("bank", "From Bank"),
        ("manual", "Manual"),
    )

    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        related_name="mcqs"
    )

    source_type = models.CharField(
        max_length=10,
        choices=SOURCE_TYPES
    )

    bank_question = models.ForeignKey(
        MCQBank,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    question_text = models.TextField()

    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)

    correct_option = models.CharField(max_length=1)

    marks = models.PositiveIntegerField(default=1)

    order = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.exam.title} - MCQ"
    
# =========================================================
# 🔥 EXAM SHORT ANSWER (ATTACHED TO SPECIFIC EXAM)
# =========================================================
class ExamShortAnswer(models.Model):

    SOURCE_TYPES = (
        ("bank", "From Bank"),
        ("manual", "Manual"),
    )

    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        related_name="short_answers"
    )

    source_type = models.CharField(
        max_length=10,
        choices=SOURCE_TYPES
    )

    bank_question = models.ForeignKey(
        ShortAnswerBank,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    question_text = models.TextField()

    marks = models.PositiveIntegerField(default=5)

    order = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.exam.title} - Short Answer"
    
# =========================================================
# 🔥 EXAM SPOTTING (QUESTION 1)
# =========================================================
class ExamSpotting(models.Model):

    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        related_name="spotting_questions"
    )

    image = models.ImageField(
        upload_to="exam_spotting/"
    )

    marks = models.PositiveIntegerField(default=1)

    order = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.exam.title} - Spotting"
    

# =========================================================
# 🔥 EXAM PRACTICAL SECTION (MAJOR / MINOR)
# =========================================================
class ExamPractical(models.Model):

    PRACTICAL_TYPES = (
        ("major", "Major Experiment"),
        ("minor", "Minor Experiment"),
    )

    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        related_name="practicals"
    )

    practical_type = models.CharField(
        max_length=10,
        choices=PRACTICAL_TYPES
    )

    # Original experiment reference (for video link etc.)
    experiment = models.ForeignKey(
        Experiment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    # Snapshot fields (so future experiment edits don’t affect paper)
    title = models.CharField(max_length=255)
    aim = models.TextField()

    marks = models.PositiveIntegerField(default=20)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.exam.title} - {self.practical_type}"

# =========================================================
# 🔥 EXAM ATTEMPT (STUDENT EXAM ENGINE)
# =========================================================
class ExamAttempt(models.Model):

    STATUS_CHOICES = (
        ("in_progress", "In Progress"),
        ("submitted", "Submitted"),
        ("approved", "Approved"),
    )

    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="exam_attempts",
        limit_choices_to={"role": "student"}
    )

    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        related_name="attempts"
    )

    # 🔥 ALL STUDENT ANSWERS STORED HERE
    answers = models.JSONField(default=dict)

    # -------------------------
    # TIMESTAMPS
    # -------------------------
    started_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)

    # -------------------------
    # STATUS
    # -------------------------
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="in_progress"
    )

    # -------------------------
    # SECTION SCORES
    # -------------------------
    mcq_score = models.FloatField(default=0)
    short_score = models.FloatField(default=0)
    spotting_score = models.FloatField(default=0)
    practical_score = models.FloatField(default=0)
    viva_score = models.FloatField(default=0)

    total_score = models.FloatField(default=0)

    # 🔥 Teacher approval required before student sees result
    teacher_approved = models.BooleanField(default=False)

    class Meta:
        unique_together = ("student", "exam")
        ordering = ["-started_at"]

    def __str__(self):
        return f"{self.student} → {self.exam.title}"