from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now
import json

from .models import (
    Experiment, 
    Exam, 
    ExamAttempt, 
    Batch, 
    BatchExperiment, 
    StudentApproval
)

D_PHARM_NUMBERS = [1, 2, 3, 7, 8, 9, 10, 15, 16, 19, 20, 23, 24, 25, 26, 29, 30, 32, 35]

# -------------------------
# STUDENT DASHBOARD
# -------------------------
def student_dashboard(request):
    if request.session.get("role") != "student":
        return redirect("/login/")

    student = request.user
    experiments = []

    # 🔥 Ensure student has roll number
    if student.roll_no:
        try:
            roll_number = int(student.roll_no)

            # 🔥 Find matching batch created by student's teacher
            batch = Batch.objects.filter(
                teacher=student.created_by,
                start_roll__lte=roll_number,
                end_roll__gte=roll_number
            ).first()

            if batch:
                assigned_experiments = BatchExperiment.objects.filter(
                    batch=batch
                ).values_list("experiment_id", flat=True)

                experiments = Experiment.objects.filter(
                    id__in=assigned_experiments,
                    is_active=True
                ).order_by("order")

                # 🔥 Plan-based filtering
                college = student.college
                if college and college.selected_plan == 'dpharm':
                    experiments = experiments.filter(number__in=D_PHARM_NUMBERS)

        except ValueError:
            # Roll number not numeric
            experiments = []

    return render(
        request,
        "student/dashboard.html",
        {
            "name": request.session.get("name"),
            "experiments": experiments,
        }
    )

# =====================================================
# 🔥 STUDENT → EXAM DASHBOARD
# =====================================================
def student_exam_dashboard(request):

    if request.session.get("role") != "student":
        return redirect("/login/")

    student = request.user

    # 🔥 Fetch active exams from student's teacher
    exams = Exam.objects.filter(
        teacher=student.created_by,
        is_active=True
    )

    exam_data = []

    for exam in exams:

        attempt = ExamAttempt.objects.filter(
            student=student,
            exam=exam
        ).first()

        if not attempt:
            status = "Not Started"
        elif attempt.status == "in_progress":
            status = "In Progress"
        elif attempt.status == "submitted":
            status = "Submitted"
        elif attempt.status == "approved":
            status = "Approved"
        else:
            status = "Unknown"

        exam_data.append({
            "exam": exam,
            "attempt": attempt,
            "status": status
        })

    return render(
        request,
        "student/exam_dashboard.html",
        {
            "name": request.session.get("name"),
            "exam_data": exam_data
        }
    )

# =====================================================
# 🔥 STUDENT → START / RESUME EXAM
# =====================================================
def start_exam(request, exam_id):

    if request.session.get("role") != "student":
        return redirect("/login/")

    student = request.user

    # 🔥 Fetch exam safely
    exam = get_object_or_404(
        Exam,
        id=exam_id,
        is_active=True,
        teacher=student.created_by
    )

    # 🔥 Check if attempt exists
    attempt = ExamAttempt.objects.filter(
        student=student,
        exam=exam
    ).first()

    # 🚫 If already submitted → block
    if attempt and attempt.status == "submitted":
        return redirect("/student/exams/")

    # ✅ If no attempt → create
    if not attempt:
        attempt = ExamAttempt.objects.create(
            student=student,
            exam=exam,
            status="in_progress"
        )

    # 🔥 Load exam questions
    mcqs = exam.mcqs.all()
    short_answers = exam.short_answers.all()
    spotting_questions = exam.spotting_questions.all()
    practicals = exam.practicals.all()

    return render(
        request,
        "student/start_exam.html",
        {
            "exam": exam,
            "attempt": attempt,
            "mcqs": mcqs,
            "short_answers": short_answers,
            "spotting_questions": spotting_questions,
            "practicals": practicals,
            "duration": exam.duration_minutes,
        }
    )

# =====================================================
# 🔥 STUDENT → SUBMIT EXAM
# =====================================================
@csrf_exempt
def submit_exam(request, exam_id):

    if request.method != "POST":
        return JsonResponse({"error": "Invalid method"}, status=405)

    if request.session.get("role") != "student":
        return JsonResponse({"error": "Unauthorized"}, status=401)

    student = request.user

    exam = get_object_or_404(
        Exam,
        id=exam_id,
        is_active=True,
        teacher=student.created_by
    )

    attempt = get_object_or_404(
        ExamAttempt,
        student=student,
        exam=exam
    )

    # 🚫 Prevent re-submission
    if attempt.status == "submitted":
        return JsonResponse({"error": "Already submitted"}, status=400)

    try:
        data = json.loads(request.body.decode("utf-8"))
    except Exception:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    # 🔥 Save answers JSON
    attempt.answers = data

    # ========================================
    # 🔥 AUTO EVALUATE MCQs
    # ========================================
    mcq_answers = data.get("mcq", {})
    mcq_score = 0

    for mcq in exam.mcqs.all():
        selected = mcq_answers.get(str(mcq.id))
        if selected and selected == mcq.correct_option:
            mcq_score += int(mcq.marks or 0)

    attempt.mcq_score = mcq_score

    # 🔥 Set total score initially = MCQ score
    attempt.total_score = mcq_score

    attempt.status = "submitted"
    attempt.submitted_at = now()

    attempt.save()

    return JsonResponse({
        "status": "success",
        "redirect": "/student/exams/"
    })

# -------------------------
# EXPERIMENT INTRO PAGE
# -------------------------
def experiment_intro(request, slug):

    # 🔥 UPDATED: Allow student + admin + superadmin
    role = request.session.get("role")
    if role not in ["student", "teacher", "admin", "superadmin"]:
        return redirect("/login/")

    experiment = get_object_or_404(
        Experiment,
        slug=slug,
        is_active=True
    )

    # 🔥 Plan-based Access Control
    if role != "superadmin":
        college = request.user.college
        if college and college.selected_plan == 'dpharm':
            if experiment.number not in D_PHARM_NUMBERS:
                return redirect("/login/")

    return render(
        request,
        f"experiments/{slug}/intro.html",
        {
            "experiment": experiment,
            "demo_mode": role in ["admin", "superadmin"]  # optional for banner
        }
    )


# -------------------------
# EXPERIMENT RUN PAGE
# -------------------------
def experiment_run(request, slug):

    # 🔥 UPDATED: Allow student + admin + superadmin
    role = request.session.get("role")
    if role not in ["student", "teacher", "admin", "superadmin"]:
        return redirect("/login/")

    experiment = get_object_or_404(
        Experiment,
        slug=slug,
        is_active=True
    )

    # 🔥 Plan-based Access Control
    if role != "superadmin":
        college = request.user.college
        if college and college.selected_plan == 'dpharm':
            if experiment.number not in D_PHARM_NUMBERS:
                return redirect("/login/")

    return render(
        request,
        f"experiments/{slug}/experiment.html",
        {
            "experiment": experiment,
            "demo_mode": role in ["admin", "superadmin"]  # optional for banner
        }
    )


# -------------------------
# EXPERIMENT CONCLUSION PAGE
# -------------------------
def experiment_conclusion(request, slug):

    # 🔥 UPDATED: Allow student + admin + superadmin
    role = request.session.get("role")
    if role not in ["student", "teacher", "admin", "superadmin"]:
        return redirect("/login/")

    experiment = get_object_or_404(
        Experiment,
        slug=slug,
        is_active=True
    )

    # 🔥 Plan-based Access Control
    if role != "superadmin":
        college = request.user.college
        if college and college.selected_plan == 'dpharm':
            if experiment.number not in D_PHARM_NUMBERS:
                return redirect("/login/")

    return render(
        request,
        f"experiments/{slug}/conclusion.html",
        {
            "experiment": experiment,
            "demo_mode": role in ["admin", "superadmin"]  # optional
        }
    )

# =====================================================
# 🔥 STUDENT → VIEW EXAM RESULT
# =====================================================
def student_view_result(request, exam_id):

    if request.session.get("role") != "student":
        return redirect("/login/")

    student = request.user

    attempt = get_object_or_404(
        ExamAttempt,
        student=student,
        exam_id=exam_id,
        status="approved",
        teacher_approved=True
    )

    return render(
        request,
        "student/view_result.html",
        {
            "attempt": attempt,
            "exam": attempt.exam
        }
    )
