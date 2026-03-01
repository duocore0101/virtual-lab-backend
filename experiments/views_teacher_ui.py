from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.hashers import make_password
from django.http import HttpResponse
import csv
from experiments.models import StudentApproval
from accounts.models import User
from .models import (
    Batch,
    BatchExperiment,
    ShortAnswerBank,
    Exam,
    ExamMCQ,
    ExamShortAnswer,
    MCQBank,
    Experiment, 
    ExperimentAttempt,
    ExamSpotting,
    ExamPractical,
)


# =====================================================
# TEACHER DASHBOARD (CARD VIEW ONLY)
# =====================================================
def teacher_dashboard(request):
    if request.session.get("role") != "teacher":
        return redirect("/login/")

    teacher = request.user

    students = User.objects.filter(
        role="student",
        created_by=teacher,
        college=teacher.college
    )

    experiments = Experiment.objects.filter(
        is_active=True
    ).order_by("name")

    attempts = ExperimentAttempt.objects.filter(
        experiment__is_active=True,
        completed_at__isnull=False
    )

    return render(
        request,
        "teacher/dashboard.html",
        {
            "name": teacher.first_name,
            "total_students": students.count(),
            "total_experiments": experiments.count(),
            "total_attempts": attempts.count(),
        }
    )


# =====================================================
# TEACHER → STUDENTS LIST
# =====================================================
def teacher_students(request):
    if request.session.get("role") != "teacher":
        return redirect("/login/")

    students = User.objects.filter(
        role="student",
        created_by=request.user,
        college=request.user.college
    ).order_by("first_name")

    return render(
        request,
        "teacher/students.html",
        {
            "students": students
        }
    )


# =====================================================
# TEACHER → EXPERIMENTS LIST
# =====================================================
def teacher_experiments(request):
    if request.session.get("role") != "teacher":
        return redirect("/login/")

    experiments = Experiment.objects.filter(
        is_active=True
    ).order_by("name")

    return render(
        request,
        "teacher/experiments.html",
        {
            "experiments": experiments
        }
    )


# =====================================================
# TEACHER → ATTEMPTS LIST
# =====================================================
def teacher_attempts(request):
    if request.session.get("role") != "teacher":
        return redirect("/login/")

    attempts = ExperimentAttempt.objects.filter(
        experiment__is_active=True,
        completed_at__isnull=False
    ).select_related(
        "student",
        "experiment"
    ).order_by("-completed_at")

    return render(
        request,
        "teacher/attempts.html",
        {
            "attempts": attempts
        }
    )


# =====================================================
# CREATE STUDENT (TEACHER → STUDENT)
# =====================================================
def create_student(request):
    if request.session.get("role") != "teacher":
        return redirect("/login/")

    teacher = request.user

    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if not all([name, email, password]):
            return render(
                request,
                "teacher/create_student.html",
                {"error": "All fields are required"}
            )

        if User.objects.filter(email=email).exists():
            return render(
                request,
                "teacher/create_student.html",
                {"error": "Student with this email already exists"}
            )

        User.objects.create(
            username=email,
            email=email,
            first_name=name,
            role="student",
            college=teacher.college,
            created_by=teacher,
            password=make_password(password)
        )

        return redirect("/teacher/dashboard/")

    return render(request, "teacher/create_student.html")


# =====================================================
# CSV EXPORT → STUDENTS
# =====================================================
def teacher_export_students_csv(request):
    if request.session.get("role") != "teacher":
        return redirect("/login/")

    students = User.objects.filter(
        role="student",
        created_by=request.user,
        college=request.user.college
    )

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="students.csv"'

    writer = csv.writer(response)
    writer.writerow(["Name", "Email", "Active"])

    for s in students:
        writer.writerow([
            s.first_name,
            s.email,
            "Yes" if s.is_active else "No"
        ])

    return response


# =====================================================
# CSV EXPORT → ATTEMPTS
# =====================================================
def teacher_export_attempts_csv(request):
    if request.session.get("role") != "teacher":
        return redirect("/login/")

    attempts = ExperimentAttempt.objects.filter(
        experiment__is_active=True,
        completed_at__isnull=False
    )

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="attempts.csv"'

    writer = csv.writer(response)
    writer.writerow(["Student", "Experiment", "Completed At"])

    for a in attempts:
        writer.writerow([
            a.student.first_name,
            a.experiment.name,
            a.completed_at
        ])

    return response

# =====================================================
# 🔥 TEACHER → STUDENT APPROVAL REQUESTS (NEW FEATURE)
# =====================================================
def teacher_student_requests(request):
    if request.session.get("role") != "teacher":
        return redirect("/login/")

    pending_approvals = StudentApproval.objects.filter(
        selected_teacher=request.user,
        approval_status="pending"
    ).select_related("student")

    return render(
        request,
        "teacher/student_requests.html",
        {
            "pending_approvals": pending_approvals
        }
    )


# =====================================================
# 🔥 TEACHER → APPROVE STUDENT REQUEST
# =====================================================
def approve_student_request(request, student_id):
    if request.session.get("role") != "teacher":
        return redirect("/login/")

    approval = get_object_or_404(
        StudentApproval,
        student__id=student_id,
        selected_teacher=request.user,
        approval_status="pending"
    )

    # Update approval record
    approval.approval_status = "approved"
    approval.approved_by_teacher = True
    approval.save()

    # Activate student
    student = approval.student
    student.is_active = True
    student.save()

    return redirect("/teacher/student-requests/")


# =====================================================
# 🔥 TEACHER → REJECT STUDENT REQUEST
# =====================================================
def reject_student_request(request, student_id):
    if request.session.get("role") != "teacher":
        return redirect("/login/")

    approval = get_object_or_404(
        StudentApproval,
        student__id=student_id,
        selected_teacher=request.user,
        approval_status="pending"
    )

    approval.approval_status = "rejected"
    approval.save()

    # Keep student inactive
    student = approval.student
    student.is_active = False
    student.save()

    return redirect("/teacher/student-requests/")

# =====================================================
# 🔥 TEACHER → MANAGE BATCHES
# =====================================================
def teacher_manage_batches(request):
    if request.session.get("role") != "teacher":
        return redirect("/login/")

    batches = Batch.objects.filter(
        teacher=request.user
    ).order_by("-created_at")

    return render(
        request,
        "teacher/manage_batches.html",
        {
            "batches": batches
        }
    )


# =====================================================
# 🔥 TEACHER → CREATE BATCH
# =====================================================
def teacher_create_batch(request):
    if request.session.get("role") != "teacher":
        return redirect("/login/")

    if request.method == "POST":
        name = request.POST.get("name")
        start_roll = request.POST.get("start_roll")
        end_roll = request.POST.get("end_roll")

        if not all([name, start_roll, end_roll]):
            return redirect("/teacher/manage-batches/")

        Batch.objects.create(
            teacher=request.user,
            name=name,
            start_roll=int(start_roll),
            end_roll=int(end_roll),
        )

        return redirect("/teacher/manage-batches/")

    return redirect("/teacher/manage-batches/")


# =====================================================
# 🔥 TEACHER → EDIT BATCH
# =====================================================
def teacher_edit_batch(request, batch_id):
    if request.session.get("role") != "teacher":
        return redirect("/login/")

    batch = get_object_or_404(
        Batch,
        id=batch_id,
        teacher=request.user
    )

    if request.method == "POST":
        batch.name = request.POST.get("name")
        batch.start_roll = int(request.POST.get("start_roll"))
        batch.end_roll = int(request.POST.get("end_roll"))
        batch.save()

        return redirect("/teacher/manage-batches/")

    return render(
        request,
        "teacher/edit_batch.html",
        {
            "batch": batch
        }
    )


# =====================================================
# 🔥 TEACHER → ASSIGN PRACTICAL TO BATCH
# =====================================================
def teacher_assign_practical(request, batch_id):
    if request.session.get("role") != "teacher":
        return redirect("/login/")

    batch = get_object_or_404(
        Batch,
        id=batch_id,
        teacher=request.user
    )

    experiments = Experiment.objects.filter(
        is_active=True
    ).order_by("name")

    if request.method == "POST":
        selected_experiments = request.POST.getlist("experiments")

        # Remove old assignments
        BatchExperiment.objects.filter(batch=batch).delete()

        for exp_id in selected_experiments:
            BatchExperiment.objects.create(
                batch=batch,
                experiment_id=exp_id
            )

        return redirect("/teacher/manage-batches/")

    assigned_ids = BatchExperiment.objects.filter(
        batch=batch
    ).values_list("experiment_id", flat=True)

    return render(
        request,
        "teacher/assign_practical.html",
        {
            "batch": batch,
            "experiments": experiments,
            "assigned_ids": assigned_ids
        }
    )   

def teacher_exams(request):
    if request.session.get("role") != "teacher":
        return redirect("/login/")

    exams = Exam.objects.filter(
        teacher=request.user
    )

    return render(
        request,
        "teacher/exams.html",
        {
            "exams": exams
        }
    )

def teacher_create_exam(request):
    if request.session.get("role") != "teacher":
        return redirect("/login/")

    if request.method == "POST":
        title = request.POST.get("title")
        exam_type = request.POST.get("exam_type")
        year = request.POST.get("year")
        duration = request.POST.get("duration")

        if not all([title, exam_type, year, duration]):
            return redirect("/teacher/exams/")

        Exam.objects.create(
            teacher=request.user,
            title=title,
            exam_type=exam_type,
            year=year,
            duration_minutes=int(duration)
        )

        return redirect("/teacher/exams/")

    return render(request, "teacher/create_exam.html")

def teacher_edit_exam(request, exam_id):
    if request.session.get("role") != "teacher":
        return redirect("/login/")

    exam = get_object_or_404(
        Exam,
        id=exam_id,
        teacher=request.user
    )

    if request.method == "POST":
        exam.title = request.POST.get("title")
        exam.exam_type = request.POST.get("exam_type")
        exam.year = request.POST.get("year")
        exam.duration_minutes = int(request.POST.get("duration"))
        exam.save()

        return redirect("/teacher/exams/")

    return render(
        request,
        "teacher/edit_exam.html",
        {"exam": exam}
    )

def teacher_toggle_exam(request, exam_id):
    if request.session.get("role") != "teacher":
        return redirect("/login/")

    exam = get_object_or_404(
        Exam,
        id=exam_id,
        teacher=request.user
    )

    exam.is_active = not exam.is_active
    exam.save()

    return redirect("/teacher/exams/")

def teacher_exam_builder(request, exam_id):
    if request.session.get("role") != "teacher":
        return redirect("/login/")

    exam = get_object_or_404(
        Exam,
        id=exam_id,
        teacher=request.user
    )

    # ================================
    # HANDLE POST ACTIONS
    # ================================
    if request.method == "POST":

        action = request.POST.get("action")

        # --------------------------------
# ADD SPOTTING IMAGE (ONLY D.PHARM)
# --------------------------------
        if action == "add_spotting":

            # Restrict spotting to D.Pharm only
            if exam.year != "dpharm_2":
                return redirect(request.path)

            ExamSpotting.objects.create(
                exam=exam,
                image=request.FILES.get("image"),
                marks=int(request.POST.get("marks", 1)),
                order=exam.spotting_questions.count() + 1
            )

            return redirect(request.path)
        
        # --------------------------------
        # UPDATE SPOTTING MARKS
        # --------------------------------
        elif action == "update_spotting_marks":

            if exam.year != "dpharm_2":
                return redirect(request.path)

            spot_id = request.POST.get("spot_id")
            marks = request.POST.get("marks")

            spot = get_object_or_404(
                ExamSpotting,
                id=spot_id, 
                exam=exam
            )

            spot.marks = int(marks)
            spot.save()

            return redirect(request.path)

        # --------------------------------
        # ADD MANUAL MCQ
        # --------------------------------
        elif action == "add_manual_mcq":

            ExamMCQ.objects.create(
                exam=exam,
                source_type="manual",
                question_text=request.POST.get("question_text"),
                option_a=request.POST.get("option_a"),
                option_b=request.POST.get("option_b"),
                option_c=request.POST.get("option_c"),
                option_d=request.POST.get("option_d"),
                correct_option=request.POST.get("correct_option"),
                marks=int(request.POST.get("marks", 1)),
                order=exam.mcqs.count() + 1
            )

            return redirect(request.path)

        # --------------------------------
        # ADD MANUAL SHORT ANSWER
        # --------------------------------
        elif action == "add_manual_short":

            ExamShortAnswer.objects.create(
                exam=exam,
                source_type="manual",
                question_text=request.POST.get("question_text"),
                marks=int(request.POST.get("marks", 5)),
                order=exam.short_answers.count() + 1
            )

            return redirect(request.path)

        # --------------------------------
        # ADD MCQ FROM BANK
        # --------------------------------
        elif action == "add_bank_mcq":

            selected_ids = request.POST.getlist("selected_mcqs")

            for q_id in selected_ids:
                bank_q = get_object_or_404(
                    MCQBank,
                    id=q_id,
                    is_active=True
                )

                ExamMCQ.objects.create(
                    exam=exam,
                    source_type="bank",
                    bank_question=bank_q,
                    question_text=bank_q.question_text,
                    option_a=bank_q.option_a,
                    option_b=bank_q.option_b,
                    option_c=bank_q.option_c,
                    option_d=bank_q.option_d,
                    correct_option=bank_q.correct_option,
                    marks=1,
                    order=exam.mcqs.count() + 1
                )

            return redirect(request.path)

        # --------------------------------
        # ADD SHORT ANSWER FROM BANK
        # --------------------------------
        elif action == "add_bank_short":

            selected_ids = request.POST.getlist("selected_shorts")

            for q_id in selected_ids:
                bank_q = get_object_or_404(
                    ShortAnswerBank,
                    id=q_id,
                    is_active=True
                )

                ExamShortAnswer.objects.create(
                    exam=exam,
                    source_type="bank",
                    bank_question=bank_q,
                    question_text=bank_q.question_text,
                    marks=5,
                    order=exam.short_answers.count() + 1
                )

            return redirect(request.path)

        # --------------------------------
        # UPDATE MCQ MARKS
        # --------------------------------
        elif action == "update_mcq_marks":

            mcq_id = request.POST.get("mcq_id")
            marks = request.POST.get("marks")

            mcq = get_object_or_404(
                ExamMCQ,
                id=mcq_id,
                exam=exam
            )

            mcq.marks = int(marks)
            mcq.save()

            return redirect(request.path)

        # --------------------------------
        # UPDATE SHORT MARKS
        # --------------------------------
        elif action == "update_short_marks":

            short_id = request.POST.get("short_id")
            marks = request.POST.get("marks")

            short = get_object_or_404(
                ExamShortAnswer,
                id=short_id,
                exam=exam
            )

            short.marks = int(marks)
            short.save()

            return redirect(request.path)
        # 🔥 ADD THIS BLOCK RIGHT HERE
        elif action == "update_viva_marks":

            viva_marks = request.POST.get("viva_marks")

            exam.viva_marks = int(viva_marks)
            exam.save()

            return redirect(request.path)
# --------------------------------
# ADD MAJOR / MINOR PRACTICAL
# --------------------------------
        elif action == "add_practical":

            practical_type = request.POST.get("practical_type")
            experiment_id = request.POST.get("experiment_id")
            marks = request.POST.get("marks")

            selected_experiment = get_object_or_404(
                Experiment,
                id=experiment_id,
                is_active=True
            )
        # elif action == "update_viva_marks":

        #     viva_marks = request.POST.get("viva_marks")

        #     exam.viva_marks = int(viva_marks)
        #     exam.save()

        #     return redirect(request.path)

            # Ensure only one major and one minor per exam
            if ExamPractical.objects.filter(
                exam=exam,
                practical_type=practical_type
            ).exists():
                return redirect(request.path)

            ExamPractical.objects.create(
                exam=exam,
                practical_type=practical_type,
                experiment=selected_experiment,
                title=selected_experiment.name,
                aim=selected_experiment.aim,
                marks=int(marks)
            )

            return redirect(request.path)
    # ================================
    # FINAL RENDER
    # ================================
    major_practical = exam.practicals.filter(practical_type="major").first()
    minor_practical = exam.practicals.filter(practical_type="minor").first()

    return render(
        request,
        "teacher/exam_builder.html",
        {
            "exam": exam,
            "mcq_bank": MCQBank.objects.filter(is_active=True),
            "short_bank": ShortAnswerBank.objects.filter(is_active=True),
            "mcqs": exam.mcqs.all(),
            "short_answers": exam.short_answers.all(),
            "spotting_questions": exam.spotting_questions.all(),
            "practicals": exam.practicals.all(),
            "experiments_list": Experiment.objects.filter(is_active=True),
            "major_practical": major_practical,
            "minor_practical": minor_practical,
        }
    )
    

def delete_exam_mcq(request, mcq_id):
    if request.session.get("role") != "teacher":
        return redirect("/login/")

    mcq = get_object_or_404(
        ExamMCQ,
        id=mcq_id,
        exam__teacher=request.user
    )

    exam_id = mcq.exam.id
    mcq.delete()

    return redirect(f"/teacher/exams/{exam_id}/builder/")
def delete_exam_short(request, short_id):
    if request.session.get("role") != "teacher":
        return redirect("/login/")

    short = get_object_or_404(
        ExamShortAnswer,
        id=short_id,
        exam__teacher=request.user
    )

    exam_id = short.exam.id
    short.delete()

    return redirect(f"/teacher/exams/{exam_id}/builder/")

def delete_exam_spotting(request, spot_id):
    if request.session.get("role") != "teacher":
        return redirect("/login/")

    spot = get_object_or_404(
        ExamSpotting,
        id=spot_id,
        exam__teacher=request.user
    )

    exam_id = spot.exam.id
    spot.delete()

    return redirect(f"/teacher/exams/{exam_id}/builder/")


# =====================================================
# 🔥 TEACHER → VIEW EXAM ATTEMPTS
# =====================================================
from .models import ExamAttempt

def teacher_exam_attempts(request, exam_id):

    if request.session.get("role") != "teacher":
        return redirect("/login/")

    exam = get_object_or_404(
        Exam,
        id=exam_id,
        teacher=request.user
    )

    attempts = ExamAttempt.objects.filter(
        exam=exam,
        status="submitted"
    ).select_related("student")

    return render(
        request,
        "teacher/exam_attempts.html",
        {
            "exam": exam,
            "attempts": attempts
        }
    )


# =====================================================
# 🔥 TEACHER → EVALUATE ATTEMPT
# =====================================================
def evaluate_attempt(request, attempt_id):

    if request.session.get("role") != "teacher":
        return redirect("/login/")

    attempt = get_object_or_404(
        ExamAttempt,
        id=attempt_id,
        exam__teacher=request.user
    )

    if request.method == "POST":

        short_score = float(request.POST.get("short_score", 0))
        practical_score = float(request.POST.get("practical_score", 0))
        viva_score = float(request.POST.get("viva_score", 0))

        attempt.short_score = short_score
        attempt.practical_score = practical_score
        attempt.viva_score = viva_score

        # 🔥 Final total calculation
        attempt.total_score = (
            attempt.mcq_score +
            short_score +
            practical_score +
            viva_score
        )

        attempt.status = "approved"
        attempt.teacher_approved = True
        attempt.save()

        return redirect("/teacher/exams/")

    return render(
        request,
        "teacher/evaluate_attempt.html",
        {
            "attempt": attempt,
            "answers": attempt.answers
        }
    )