from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.hashers import make_password
from accounts.models import User, College, PrincipalRequest
from .models import Experiment, ExperimentAttempt, AuditLog
from django.db.models import Q
from django.http import JsonResponse


# =====================================================
# SUPER ADMIN DASHBOARD (GLOBAL VIEW)
# =====================================================
def superadmin_dashboard(request):
    if request.session.get("role") != "superadmin":
        return redirect("/login/")

    context = {
        "name": request.session.get("name"),

        # -------------------------
        # CARD COUNTS (ACTIVE ONLY)
        # -------------------------
        "total_colleges": College.objects.filter(is_active=True).count(),
        "total_admins": User.objects.filter(role="admin", is_active=True).count(),
        "total_teachers": User.objects.filter(role="teacher", is_active=True).count(),
        "total_students": User.objects.filter(role="student", is_active=True).count(),
        "total_experiments": Experiment.objects.count(),
        "total_attempts": ExperimentAttempt.objects.filter(
            completed_at__isnull=False
        ).count(),

        # -------------------------
        # 🔥 NEW: Pending Principal Requests Count
        # -------------------------
        "pending_requests": PrincipalRequest.objects.filter(status="pending").count(),

        # -------------------------
        # COLLEGE ADMINS TABLE
        # -------------------------
        "admins": User.objects.filter(
            role="admin"
        ).select_related("college").order_by("college__name"),
    }

    return render(request, "superadmin/dashboard.html", context)


# =====================================================
# 🔥 SUPER ADMIN – PRINCIPAL REQUEST LIST
# =====================================================
def superadmin_principal_requests(request):
    if request.session.get("role") != "superadmin":
        return redirect("/login/")

    requests = PrincipalRequest.objects.all().order_by("-created_at")

    return render(
        request,
        "superadmin/principal_requests.html",
        {"requests": requests}
    )


# =====================================================
# 🔥 APPROVE PRINCIPAL REQUEST
# =====================================================
def approve_principal_request(request, request_id):
    if request.session.get("role") != "superadmin":
        return redirect("/login/")

    principal_request = get_object_or_404(
        PrincipalRequest,
        id=request_id,
        status="pending"
    )

    # Generate unique college code
    college_code = principal_request.college_name.lower().replace(" ", "_")

    if College.objects.filter(code=college_code).exists():
        college_code = f"{college_code}_{principal_request.id}"

    # Create College
    college = College.objects.create(
        name=principal_request.college_name,
        code=college_code,
        is_active=True
    )

    # Create Admin User (Password already hashed)
    admin_user = User.objects.create(
        username=principal_request.email,
        email=principal_request.email,
        first_name=principal_request.fullname,
        role="admin",
        college=college,
        created_by=request.user,
        is_active=True,
        password=principal_request.password
    )

    # Update Request Status
    principal_request.status = "approved"
    principal_request.save()

    # Audit Log
    AuditLog.objects.create(
        actor=request.user,
        target_user=admin_user,
        action="create",
        message="Approved principal registration request"
    )

    return redirect("/superadmin/principal-requests/")


# =====================================================
# 🔥 REJECT PRINCIPAL REQUEST
# =====================================================
def reject_principal_request(request, request_id):
    if request.session.get("role") != "superadmin":
        return redirect("/login/")

    principal_request = get_object_or_404(
        PrincipalRequest,
        id=request_id,
        status="pending"
    )

    principal_request.status = "rejected"
    principal_request.save()

    return redirect("/superadmin/principal-requests/")


# =====================================================
# CREATE ADMIN (SUPER ADMIN → COLLEGE ADMIN)
# =====================================================
def create_admin(request):
    if request.session.get("role") != "superadmin":
        return redirect("/login/")

    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        college_name = request.POST.get("college_name")
        college_code = request.POST.get("college_code")

        if not all([name, email, password, college_name, college_code]):
            return render(request, "superadmin/create_admin.html", {
                "error": "All fields are required"
            })

        if User.objects.filter(email=email).exists():
            return render(request, "superadmin/create_admin.html", {
                "error": "Admin with this email already exists"
            })

        if College.objects.filter(code=college_code).exists():
            return render(request, "superadmin/create_admin.html", {
                "error": "College code already exists"
            })

        college = College.objects.create(
            name=college_name,
            code=college_code,
            is_active=True
        )

        User.objects.create(
            username=email,
            email=email,
            first_name=name,
            role="admin",
            college=college,
            created_by=request.user,
            is_active=True,
            password=make_password(password)
        )

        return redirect("/superadmin/dashboard/")

    return render(request, "superadmin/create_admin.html")


# =====================================================
# CLICKABLE CARD PAGES (EXISTING)
# =====================================================
def superadmin_colleges(request):
    if request.session.get("role") != "superadmin":
        return redirect("/login/")

    query = request.GET.get("q", "")

    colleges = College.objects.all().order_by("name")

    if query:
        colleges = colleges.filter(name__icontains=query)

    # 🔥 If AJAX request → return JSON
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        data = []
        for college in colleges:
            data.append({
                "id": college.id,
                "name": college.name,
                "is_active": college.is_active
            })
        return JsonResponse({"colleges": data})

    return render(
        request,
        "superadmin/colleges.html",
        {
            "colleges": colleges
        }
    )

def superadmin_admins(request):
    if request.session.get("role") != "superadmin":
        return redirect("/login/")

    admins = User.objects.filter(
        role="admin"
    ).select_related("college").order_by("college__name")

    return render(request, "superadmin/admins.html", {"admins": admins})


def superadmin_teachers(request):
    if request.session.get("role") != "superadmin":
        return redirect("/login/")

    teachers = User.objects.filter(
        role="teacher"
    ).select_related("college").order_by("first_name")

    return render(request, "superadmin/teachers.html", {"teachers": teachers})


def superadmin_students(request):
    if request.session.get("role") != "superadmin":
        return redirect("/login/")

    students = User.objects.filter(
        role="student"
    ).select_related("college", "created_by").order_by("first_name")

    return render(request, "superadmin/students.html", {"students": students})


def superadmin_experiments(request):
    if request.session.get("role") != "superadmin":
        return redirect("/login/")

    experiments = Experiment.objects.select_related("teacher").order_by("name")
    return render(request, "superadmin/experiments.html", {"experiments": experiments})


def superadmin_attempts(request):
    if request.session.get("role") != "superadmin":
        return redirect("/login/")

    attempts = ExperimentAttempt.objects.filter(
        completed_at__isnull=False
    ).select_related(
        "student", "experiment", "experiment__teacher"
    ).order_by("-completed_at")

    return render(request, "superadmin/attempts.html", {"attempts": attempts})


# =====================================================
# SUPER ADMIN – USERS (COMBINED VIEW)
# =====================================================
def superadmin_users(request):
    if request.session.get("role") != "superadmin":
        return redirect("/login/")

    users = User.objects.select_related("college").order_by("role", "first_name")
    return render(request, "superadmin/users.html", {"users": users})

# =====================================================
# SUPER ADMIN – REPORTS
# =====================================================
def superadmin_reports(request):
    if request.session.get("role") != "superadmin":
        return redirect("/login/")

    return render(request, "superadmin/reports.html")


# =====================================================
# SUPER ADMIN – BILLING
# =====================================================
def superadmin_billing(request):
    if request.session.get("role") != "superadmin":
        return redirect("/login/")

    return render(request, "superadmin/billing.html")


# =====================================================
# SUPER ADMIN – CMS
# =====================================================
def superadmin_cms(request):
    if request.session.get("role") != "superadmin":
        return redirect("/login/")

    return render(request, "superadmin/cms.html")


# =====================================================
# SUPER ADMIN – SUPPORT
# =====================================================
def superadmin_support(request):
    if request.session.get("role") != "superadmin":
        return redirect("/login/")

    return render(request, "superadmin/support.html")


# =====================================================
# SUPER ADMIN – SETTINGS
# =====================================================
def superadmin_settings(request):
    if request.session.get("role") != "superadmin":
        return redirect("/login/")

    return render(request, "superadmin/settings.html")


# =====================================================
# SUPER ADMIN – AUDIT LOGS
# =====================================================
def superadmin_audit_logs(request):
    if request.session.get("role") != "superadmin":
        return redirect("/login/")

    logs = AuditLog.objects.select_related(
        "actor", "target_user"
    ).all()

    return render(request, "superadmin/audit_logs.html", {"logs": logs})

# =====================================================
# SUPER ADMIN – COLLEGE DETAIL (SHOW TEACHERS)
# =====================================================
def superadmin_college_detail(request, college_id):
    if request.session.get("role") != "superadmin":
        return redirect("/login/")

    college = get_object_or_404(College, id=college_id)

    teachers = User.objects.filter(
        role="teacher",
        college=college
    )

    return render(
        request,
        "superadmin/college_detail.html",
        {
            "college": college,
            "teachers": teachers,
            "total_teachers": teachers.count()
        }
    )


# =====================================================
# SUPER ADMIN – TEACHER DETAIL (SHOW STUDENTS)
# =====================================================
def superadmin_teacher_detail(request, teacher_id):
    if request.session.get("role") != "superadmin":
        return redirect("/login/")

    teacher = get_object_or_404(
        User,
        id=teacher_id,
        role="teacher"
    )

    students = User.objects.filter(
        role="student",
        created_by=teacher
    )

    return render(
        request,
        "superadmin/teacher_detail.html",
        {
            "teacher": teacher,
            "students": students,
            "total_students": students.count()
        }
    )
# =====================================================
# TOGGLES (UNCHANGED)
# =====================================================
def superadmin_toggle_user(request, user_id):
    if request.session.get("role") != "superadmin":
        return redirect("/login/")

    user = get_object_or_404(User, id=user_id)

    if user.id == request.user.id:
        return redirect(request.META.get("HTTP_REFERER", "/superadmin/dashboard/"))

    user.is_active = not user.is_active
    user.save()

    return redirect(request.META.get("HTTP_REFERER", "/superadmin/dashboard/"))


def superadmin_toggle_college(request, college_id):
    if request.session.get("role") != "superadmin":
        return redirect("/login/")

    college = get_object_or_404(College, id=college_id)
    college.is_active = not college.is_active
    college.save()

    User.objects.filter(college=college).update(is_active=college.is_active)
    return redirect("/superadmin/colleges/")