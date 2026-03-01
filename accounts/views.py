from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from .models import User, College, PrincipalRequest, TeacherRequest
# 🔥 NEW IMPORT (SAFE ADDITION)
from experiments.models import StudentApproval


# =====================================================
# LOGIN + REGISTRATION (PUBLIC)
# =====================================================
def login_view(request):

    colleges = College.objects.filter(is_active=True)
    teachers = User.objects.filter(
        role="teacher",
        is_active=True
    ).select_related("college")

    if request.method == "POST":

        action = request.POST.get("action")

        # =====================================================
        # LOGIN
        # =====================================================
        if action == "login":

            email = request.POST.get("email")
            password = request.POST.get("password")

            try:
                user_obj = User.objects.select_related("college").get(email=email)
                user = authenticate(
                    request,
                    username=user_obj.username,
                    password=password
                )
            except User.DoesNotExist:
                user = None

            if user is None:
                return render(request, "auth/login.html", {
                    "error": "Invalid email or password",
                    "colleges": colleges,
                    "teachers": teachers
                })

            if not user.is_active:
                return render(request, "auth/login.html", {
                    "error": "Your account is pending approval.",
                    "colleges": colleges,
                    "teachers": teachers
                })

            if user.role != "superadmin":
                if user.college and not user.college.is_active:
                    return render(request, "auth/login.html", {
                        "error": "Your college access has been disabled.",
                        "colleges": colleges,
                        "teachers": teachers
                    })

            login(request, user)

            request.session["user_id"] = user.id
            request.session["role"] = user.role
            request.session["name"] = user.first_name
            request.session["college_id"] = (
                user.college.id if user.college else None
            )

            if user.role == "superadmin":
                return redirect("/superadmin/dashboard/")
            elif user.role == "admin":
                return redirect("/admin/dashboard/")
            elif user.role == "teacher":
                return redirect("/teacher/dashboard/")
            elif user.role == "student":
                return redirect("/student/dashboard/")

            logout(request)
            request.session.flush()
            return redirect("/login/")

        # =====================================================
        # REGISTRATION
        # =====================================================
        elif action == "register":

            role = request.POST.get("role")
            college_id = request.POST.get("college_id")
            teacher_id = request.POST.get("teacher_id")
            college_name = request.POST.get("college_name")
            fullname = request.POST.get("fullname")
            email = request.POST.get("email")
            mobile = request.POST.get("mobile")
            roll_no = request.POST.get("roll_no")  # 🔥 NEW SAFE ADDITION
            password = request.POST.get("password")
            confirm_password = request.POST.get("confirm_password")

            # -------------------------
            # VALIDATION
            # -------------------------
            if password != confirm_password:
                return render(request, "auth/login.html", {
                    "error": "Passwords do not match",
                    "colleges": colleges,
                    "teachers": teachers
                })

            if User.objects.filter(email=email).exists():
                return render(request, "auth/login.html", {
                    "error": "User with this email already exists",
                    "colleges": colleges,
                    "teachers": teachers
                })

            if not role:
                return render(request, "auth/login.html", {
                    "error": "Please select a role",
                    "colleges": colleges,
                    "teachers": teachers
                })

            # =====================================================
            # 🔥 PRINCIPAL REGISTRATION (SUPERADMIN APPROVAL)
            # =====================================================
            if role == "admin":

                if PrincipalRequest.objects.filter(email=email, status="pending").exists():
                    return render(request, "auth/login.html", {
                        "error": "Your approval request is already pending.",
                        "colleges": colleges,
                        "teachers": teachers
                    })

                if not college_name:
                    return render(request, "auth/login.html", {
                        "error": "Please enter college name",
                        "colleges": colleges,
                        "teachers": teachers
                    })

                PrincipalRequest.objects.create(
                    fullname=fullname,
                    email=email,
                    mobile=mobile,
                    college_name=college_name,
                    password=make_password(password),
                    status="pending"
                )

                return render(request, "auth/login.html", {
                    "message": "Your registration request has been sent to Superadmin for approval.",
                    "colleges": colleges,
                    "teachers": teachers
                })

            # =====================================================
            # 🔥 TEACHER REGISTRATION (ADMIN APPROVAL)
            # =====================================================
            elif role == "teacher":

                if not college_id:
                    return render(request, "auth/login.html", {
                        "error": "Please select a college",
                        "colleges": colleges,
                        "teachers": teachers
                    })

                college = College.objects.get(id=college_id)

                if TeacherRequest.objects.filter(email=email, status="pending").exists():
                    return render(request, "auth/login.html", {
                        "error": "Your approval request is already pending.",
                        "colleges": colleges,
                        "teachers": teachers
                    })

                TeacherRequest.objects.create(
                    fullname=fullname,
                    email=email,
                    mobile=mobile,
                    college=college,
                    password=make_password(password),
                    status="pending"
                )

                return render(request, "auth/login.html", {
                    "message": "Registration successful. Waiting for Admin approval.",
                    "colleges": colleges,
                    "teachers": teachers
                })

            # =====================================================
            # 🔥 STUDENT REGISTRATION (TEACHER LINKED + APPROVAL)
            # =====================================================
            elif role == "student":

                if not college_id:
                    return render(request, "auth/login.html", {
                        "error": "Please select a college",
                        "colleges": colleges,
                        "teachers": teachers
                    })

                if not teacher_id:
                    return render(request, "auth/login.html", {
                        "error": "Please select a teacher",
                        "colleges": colleges,
                        "teachers": teachers
                    })

                college = College.objects.get(id=college_id)
                created_by_user = User.objects.get(id=teacher_id)

                # 🔥 CREATE STUDENT (EXISTING LOGIC UNCHANGED)
                student = User.objects.create(
                    username=email,
                    email=email,
                    first_name=fullname,
                    role="student",
                    college=college,
                    created_by=created_by_user,
                    is_active=False,
                    mobile=mobile,      # 🔥 NEW
                    roll_no=roll_no,    # 🔥 NEW
                    password=make_password(password)
                )

                # 🔥 CREATE TEACHER APPROVAL ENTRY
                StudentApproval.objects.create(
                    student=student,
                    selected_teacher=created_by_user,
                    approval_status="pending",
                    approved_by_teacher=False
                )

                return render(request, "auth/login.html", {
                    "message": "Registration successful. Waiting for approval.",
                    "colleges": colleges,
                    "teachers": teachers
                })

    return render(request, "auth/login.html", {
        "colleges": colleges,
        "teachers": teachers
    })


# =====================================================
# LOGOUT
# =====================================================
def logout_view(request):
    logout(request)
    request.session.flush()
    return redirect("/login/")