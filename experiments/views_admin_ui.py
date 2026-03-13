from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.hashers import make_password
from django.http import HttpResponse
from django.db.models import Count
from django.utils.timezone import now
import csv
# 🔥 UPDATED IMPORT
from accounts.models import User, TeacherRequest
from .models import Experiment, ExperimentAttempt, AuditLog

D_PHARM_NUMBERS = [1, 2, 3, 7, 8, 9, 10, 15, 16, 19, 20, 23, 24, 25, 26, 29, 30, 32, 35]


# =====================================================
# ADMIN DASHBOARD (COLLEGE SCOPED)
# =====================================================
def admin_dashboard(request):
    if request.session.get("role") != "admin":
        return redirect("/login/")

    admin = request.user
    college = admin.college

    teachers = User.objects.filter(
        role="teacher",
        college=college,
        is_active=True
    ).order_by("first_name")

    students = User.objects.filter(
        role="student",
        college=college,
        is_active=True
    )

    experiments = Experiment.objects.filter(
        teacher__college=college
    )

    # 🔥 Plan-based filtering
    if college.selected_plan == 'dpharm':
        experiments = experiments.filter(number__in=D_PHARM_NUMBERS)
    elif college.selected_plan == 'single':
        # For 'single', we might need a specific experiment ID assigned to the college.
        # For now, let's keep it empty or handle it if we have more info.
        pass

    attempts = ExperimentAttempt.objects.filter(
        experiment__teacher__college=college,
        completed_at__isnull=False
    )

    # 🔥 NEW: Pending Teacher Requests (NO LOGIC CHANGED)
    pending_teacher_requests = TeacherRequest.objects.filter(
        college=college,
        status="pending"
    ).count()

    avg_attempts = 0
    if students.count() > 0:
        avg_attempts = round(attempts.count() / students.count(), 2)

    experiment_data = []
    for exp in experiments:
        experiment_data.append({
            "id": exp.id,
            "name": exp.name,
            "status": exp.is_active,
            "attempts": attempts.filter(experiment=exp).count(),
        })

    return render(
        request,
        "admin/dashboard.html",
        {
            "name": request.session.get("name"),

            # Cards
            "total_teachers": teachers.count(),
            "total_students": students.count(),
            "total_attempts": attempts.count(),
            "avg_attempts": avg_attempts,

            # 🔥 NEW CARD
            "pending_teacher_requests": pending_teacher_requests,

            # Tables
            "experiments": experiment_data,
            "teachers": teachers,
            "students": students,
            "attempts": attempts.order_by("-completed_at")[:10],
        }
    )


# =====================================================
# 🔥 NEW: ADMIN → TEACHER REQUEST LIST
# =====================================================
def admin_teacher_requests(request):
    if request.session.get("role") != "admin":
        return redirect("/login/")

    requests = TeacherRequest.objects.filter(
        college=request.user.college
    ).order_by("-created_at")

    return render(
        request,
        "admin/teacher_requests.html",
        {"requests": requests}
    )


# =====================================================
# 🔥 NEW: ADMIN → APPROVE TEACHER REQUEST
# =====================================================
def approve_teacher_request(request, request_id):
    if request.session.get("role") != "admin":
        return redirect("/login/")

    teacher_request = get_object_or_404(
        TeacherRequest,
        id=request_id,
        status="pending",
        college=request.user.college
    )

    teacher = User.objects.create(
        username=teacher_request.email,
        email=teacher_request.email,
        first_name=teacher_request.fullname,
        role="teacher",
        college=request.user.college,
        created_by=request.user,
        subject=teacher_request.subject,
        is_active=True,
        password=teacher_request.password
    )

    teacher_request.status = "approved"
    teacher_request.save()

    # 🔥 Audit Log Entry
    AuditLog.objects.create(
        actor=request.user,
        target_user=teacher,
        action="create",
        message="Approved teacher registration request"
    )

    return redirect("/admin/teacher-requests/")


# =====================================================
# 🔥 NEW: ADMIN → REJECT TEACHER REQUEST
# =====================================================
def reject_teacher_request(request, request_id):
    if request.session.get("role") != "admin":
        return redirect("/login/")

    teacher_request = get_object_or_404(
        TeacherRequest,
        id=request_id,
        status="pending",
        college=request.user.college
    )

    teacher_request.status = "rejected"
    teacher_request.save()

    return redirect("/admin/teacher-requests/")

# =====================================================
# ADMIN → TOGGLE USER (ACTIVATE / DEACTIVATE)
# =====================================================
def admin_toggle_user(request, user_id):
    if request.session.get("role") != "admin":
        return redirect("/login/")

    admin = request.user

    user = get_object_or_404(
        User,
        id=user_id,
        college=admin.college
    )

    # ❌ Prevent admin disabling himself
    if user.id == admin.id:
        return redirect("/admin/dashboard/")

    user.is_active = not user.is_active
    user.save()

    return redirect(request.META.get("HTTP_REFERER", "/admin/dashboard/"))


# =====================================================
# ADMIN → TEACHERS LIST
# =====================================================
def admin_teachers(request):
    if request.session.get("role") != "admin":
        return redirect("/login/")

    teachers = User.objects.filter(
        role="teacher",
        college=request.user.college
    ).order_by("first_name")

    return render(
        request,
        "admin/teachers.html",
        {
            "teachers": teachers
        }
    )


# =====================================================
# ADMIN → STUDENTS LIST
# =====================================================
def admin_students(request):
    if request.session.get("role") != "admin":
        return redirect("/login/")

    students = User.objects.filter(
        role="student",
        college=request.user.college
    ).select_related("created_by").order_by("first_name")

    return render(
        request,
        "admin/students.html",
        {
            "students": students
        }
    )


# =====================================================
# ADMIN → EXPERIMENTS LIST
# =====================================================
def admin_experiments(request):
    if request.session.get("role") not in ["admin", "superadmin"]:
        return redirect("/login/")

    # 🔥 Plan-based filtering
    experiments = Experiment.objects.select_related("teacher").order_by("name")

    selected_plan = 'combo'
    if request.session.get("role") == "admin":
        college = request.user.college
        selected_plan = college.selected_plan
        if selected_plan == 'dpharm':
            experiments = experiments.filter(number__in=D_PHARM_NUMBERS)
        elif selected_plan == 'single':
            # Handle single experiment plan
            pass

    return render(
        request,
        "admin/experiments.html",
        {
            "experiments": experiments,
            "selected_plan": selected_plan
        }
    )

# =====================================================
# ADMIN → ATTEMPTS LIST
# =====================================================
def admin_attempts(request):
    if request.session.get("role") != "admin":
        return redirect("/login/")

    attempts = ExperimentAttempt.objects.filter(
        experiment__teacher__college=request.user.college,
        completed_at__isnull=False
    ).select_related(
        "student",
        "experiment",
        "experiment__teacher"
    ).order_by("-completed_at")

    return render(
        request,
        "admin/attempts.html",
        {
            "attempts": attempts
        }
    )


# =====================================================
# TEACHER DETAIL (ADMIN VIEW)
# =====================================================
def teacher_detail_admin(request, teacher_id):
    if request.session.get("role") != "admin":
        return redirect("/login/")

    teacher = get_object_or_404(
        User,
        id=teacher_id,
        role="teacher",
        college=request.user.college
    )

    # Assigned Experiments
    experiments = Experiment.objects.filter(teacher=teacher)

    # Completed Attempts
    attempts = ExperimentAttempt.objects.filter(
        experiment__teacher=teacher,
        completed_at__isnull=False
    ).select_related(
        "student",
        "experiment"
    ).order_by("-completed_at")

    # 🔥 Students under this teacher
    students = User.objects.filter(
        role="student",
        created_by=teacher,
        college=request.user.college
    ).order_by("first_name")

    total_students = students.count()
    active_students = students.filter(is_active=True).count()
    total_attempts = attempts.count()

    return render(
        request,
        "admin/teacher_detail.html",
        {
            "teacher": teacher,
            "experiments": experiments,
            "attempts": attempts,
            "students": students,  # 🔥 NEW
            "total_students": total_students,
            "active_students": active_students,
            "total_attempts": total_attempts,
        }
    )


# =====================================================
# CREATE TEACHER (ADMIN → TEACHER)
# =====================================================
def create_teacher(request):
    if request.session.get("role") != "admin":
        return redirect("/login/")

    experiments = Experiment.objects.all()

    college = request.user.college
    if college and college.selected_plan == 'dpharm':
        experiments = experiments.filter(number__in=D_PHARM_NUMBERS)
    elif college and college.selected_plan == 'single':
        # Handle single experiment plan
        pass

    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        subject_list = request.POST.getlist("subject")
        subject = ",".join(subject_list)
        assigned_experiments = request.POST.getlist("experiments")

        if User.objects.filter(email=email).exists():
            return render(
                request,
                "admin/create_teacher.html",
                {
                    "error": "Teacher with this email already exists",
                    "experiments": experiments
                }
            )

        teacher = User.objects.create(
            username=email,
            email=email,
            first_name=name,
            role="teacher",
            college=request.user.college,
            created_by=request.user,
            password=make_password(password)
        )

        if assigned_experiments:
            Experiment.objects.filter(
                id__in=assigned_experiments
            ).update(teacher=teacher)

        return redirect("/admin/dashboard/")

    return render(
        request,
        "admin/create_teacher.html",
        {
            "experiments": experiments
        }
    )


# =====================================================
# ADMIN REPORTS (FILTERS + CHARTS)
# =====================================================
def admin_reports(request):
    if request.session.get("role") != "admin":
        return redirect("/login/")

    college = request.user.college

    attempts = ExperimentAttempt.objects.filter(
        experiment__teacher__college=college,
        completed_at__isnull=False
    )

    start = request.GET.get("start")
    end = request.GET.get("end")

    if start:
        attempts = attempts.filter(completed_at__date__gte=start)
    if end:
        attempts = attempts.filter(completed_at__date__lte=end)

    daily_stats = (
        attempts
        .extra(select={'day': "DATE(completed_at)"})
        .values("day")
        .annotate(count=Count("id"))
        .order_by("day")
    )

    return render(
        request,
        "admin/reports.html",
        {
            "total_attempts": attempts.count(),
            "daily_stats": daily_stats,
        }
    )


# =====================================================
# ADMIN AUDIT LOGS (COLLEGE SCOPED)
# =====================================================
def admin_audit_logs(request):
    if request.session.get("role") != "admin":
        return redirect("/login/")

    logs = AuditLog.objects.filter(
        actor__college=request.user.college
    ).select_related("actor", "target_user").order_by("-created_at")

    return render(
        request,
        "admin/audit_logs.html",
        {
            "logs": logs
        }
    )


# =====================================================
# CSV EXPORTS
# =====================================================
def admin_export_students_csv(request):
    if request.session.get("role") != "admin":
        return redirect("/login/")

    students = User.objects.filter(
        role="student",
        college=request.user.college
    )

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="students.csv"'

    writer = csv.writer(response)
    writer.writerow(["Name", "Email", "Created By", "Active"])

    for s in students:
        writer.writerow([
            s.first_name,
            s.email,
            s.created_by.first_name if s.created_by else "",
            "Yes" if s.is_active else "No"
        ])

    return response


def admin_export_attempts_csv(request):
    if request.session.get("role") != "admin":
        return redirect("/login/")

    attempts = ExperimentAttempt.objects.filter(
        experiment__teacher__college=request.user.college,
        completed_at__isnull=False
    )

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="attempts.csv"'

    writer = csv.writer(response)
    writer.writerow(["Student", "Experiment", "Teacher", "Completed At"])

    for a in attempts:
        writer.writerow([
            a.student.first_name,
            a.experiment.name,
            a.experiment.teacher.first_name,
            a.completed_at
        ])

    return response
