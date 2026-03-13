from django.contrib import admin
from .models import (
    Experiment,
    Exam,
    MCQBank,
    ShortAnswerBank,
    ExamMCQ,
    ExamShortAnswer,
    ExamSpotting,
    SpottingBank
)

# =========================================================
# SPOTTING BANK ADMIN
# =========================================================
@admin.register(SpottingBank)
class SpottingBankAdmin(admin.ModelAdmin):
    list_display = ("name", "image_slug", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name", "image_slug")

# =========================================================
# EXAM SPOTTING
# =========================================================
@admin.register(ExamSpotting)
class ExamSpottingAdmin(admin.ModelAdmin):
    list_display = ("exam", "get_specimen_name", "marks", "order")
    
    def get_specimen_name(self, obj):
        return obj.bank_item.name if obj.bank_item else "Manual Image"
    get_specimen_name.short_description = "Specimen"

# =========================================================
# EXPERIMENT ADMIN
# =========================================================
@admin.register(Experiment)
class ExperimentAdmin(admin.ModelAdmin):
    list_display = ('name', 'experiment_type', 'teacher', 'is_active')
    list_filter = ('experiment_type', 'is_active')
    search_fields = ('name',)
    ordering = ('name',)
    prepopulated_fields = {"slug": ("name",)}


# =========================================================
# EXAM ADMIN
# =========================================================
@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ("title", "teacher", "year", "exam_type", "is_active")
    list_filter = ("year", "exam_type", "is_active")
    search_fields = ("title",)
    ordering = ("-created_at",)


# =========================================================
# MCQ BANK ADMIN (IMPROVED)
# =========================================================
@admin.register(MCQBank)
class MCQBankAdmin(admin.ModelAdmin):

    list_display = (
        "short_question",
        "topic",
        "correct_option",
        "is_active",
    )

    list_filter = ("topic", "is_active")
    search_fields = ("question_text", "topic")
    ordering = ("-created_at",)

    fieldsets = (
        ("Question", {
            "fields": ("question_text",)
        }),
        ("Options", {
            "fields": (
                "option_a",
                "option_b",
                "option_c",
                "option_d",
            )
        }),
        ("Answer Settings", {
            "fields": ("correct_option", "topic", "is_active")
        }),
    )

    def short_question(self, obj):
        return obj.question_text[:60]
    short_question.short_description = "Question"


# =========================================================
# SHORT ANSWER BANK ADMIN
# =========================================================
@admin.register(ShortAnswerBank)
class ShortAnswerBankAdmin(admin.ModelAdmin):

    list_display = (
        "short_question",
        "topic",
        "is_active",
    )

    list_filter = ("topic", "is_active")
    search_fields = ("question_text", "topic")
    ordering = ("-created_at",)

    fieldsets = (
        ("Question", {
            "fields": ("question_text",)
        }),
        ("Optional Model Answer", {
            "fields": ("model_answer",)
        }),
        ("Settings", {
            "fields": ("topic", "is_active")
        }),
    )

    def short_question(self, obj):
        return obj.question_text[:60]
    short_question.short_description = "Question"


# =========================================================
# EXAM MCQ (READ-ONLY SUPPORT)
# =========================================================
@admin.register(ExamMCQ)
class ExamMCQAdmin(admin.ModelAdmin):
    list_display = ("exam", "source_type", "marks", "order")
    list_filter = ("source_type",)
    search_fields = ("question_text",)


# =========================================================
# EXAM SHORT ANSWER
# =========================================================
@admin.register(ExamShortAnswer)
class ExamShortAnswerAdmin(admin.ModelAdmin):
    list_display = ("exam", "source_type", "marks", "order")
    list_filter = ("source_type",)
    search_fields = ("question_text",)