from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.hashers import make_password
from django.http import HttpResponse, JsonResponse
from django.utils.timezone import now
import csv
import io
import os
import openpyxl
from openpyxl.utils import get_column_letter
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from django.conf import settings
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
    SpottingBank
)

D_PHARM_NUMBERS = [1, 2, 3, 7, 8, 9, 10, 15, 16, 19, 20, 23, 24, 25, 26, 29, 30, 32, 35]

D_PHARM_NUMBERS = [1, 2, 3, 7, 8, 9, 10, 15, 16, 19, 20, 23, 24, 25, 26, 29, 30, 32, 35]


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

    subject_list = teacher.subject.split(",") if teacher.subject else []
    
    experiments = Experiment.objects.filter(is_active=True).order_by("number")

    # 🔥 Plan-based filtering
    college = teacher.college
    if college and college.selected_plan == 'dpharm':
        experiments = experiments.filter(number__in=D_PHARM_NUMBERS)

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

    subject_code = request.GET.get("subject")
    
    students = User.objects.filter(
        role="student",
        created_by=request.user,
        college=request.user.college
    ).order_by("roll_no")

    if subject_code:
        students = students.filter(subject=subject_code)

    # Subject name for header
    subject_map = {
        "dpharm_2": "2ND YR D.PHARM",
        "bpharm_4": "2ND YR B.PHARM (SEM-IV)",
        "bpharm_5": "3RD YR B.PHARM (SEM-V)",
        "bpharm_6": "3RD YR B.PHARM (SEM-VI)"
    }
    subject_name = subject_map.get(subject_code, "All Students")

    # Fetch batches to map students
    from .models import Batch
    batches = Batch.objects.filter(teacher=request.user)
    
    # Map batches to students
    for student in students:
        student.assigned_batch_name = "---"
        if student.roll_no and student.roll_no.isdigit():
            roll_int = int(student.roll_no)
            for batch in batches:
                if batch.start_roll <= roll_int <= batch.end_roll:
                    student.assigned_batch_name = batch.name
                    break

    return render(
        request,
        "teacher/students.html",
        {
            "students": students,
            "subject_name": subject_name,
            "subject_code": subject_code
        }
    )


# =====================================================
# EXPORT STUDENTS → PDF (Branded)
# =====================================================
def export_students_pdf(request):
    if request.session.get("role") != "teacher":
        return redirect("/login/")

    subject_code = request.GET.get("subject")
    teacher = request.user
    college = teacher.college

    students = User.objects.filter(
        role="student",
        created_by=teacher,
        college=college
    ).order_by("roll_no")

    if subject_code:
        students = students.filter(subject=subject_code)

    # Batch mapping logic (same as teacher_students view)
    batches = Batch.objects.filter(teacher=teacher)
    for student in students:
        student.assigned_batch_name = "---"
        if student.roll_no and student.roll_no.isdigit():
            roll_int = int(student.roll_no)
            for b in batches:
                if b.start_roll <= roll_int <= b.end_roll:
                    student.assigned_batch_name = b.name
                    break

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=50)
    elements = []
    styles = getSampleStyleSheet()

    # --- Header (Logo and Name) ---
    header_data = []
    college_name = college.name if college else "Virtual Lab System"
    college_address = college.address if college and college.address else ""
    
    logo_part = None
    if college and college.logo:
        try:
            logo_path = college.logo.path
            if os.path.exists(logo_path):
                logo_part = Image(logo_path, width=65, height=65)
        except Exception:
            pass

    name_style = ParagraphStyle(
        'CollegeNameStyle',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=22,
        textColor=colors.black,
        alignment=0, # Left
        leading=24
    )

    address_style = ParagraphStyle(
        'AddressStyle',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=9,
        textColor=colors.grey,
        alignment=0, # Left
    )
    
    # Header Content (Name + Address)
    header_info = [Paragraph(college_name, name_style)]
    if college_address:
        header_info.append(Paragraph(college_address, address_style))

    if logo_part:
        # Table for Logo and info alignment
        header_table = Table([[logo_part, header_info]], colWidths=[80, 450])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ]))
        elements.append(header_table)
    else:
        elements.extend(header_info)
    
    elements.append(Spacer(1, 15))
    
    # Horizontal Line
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#ff4b2b"), spaceAfter=15))
    
    # Title "Student List" (Centered and Underlined)
    title_style = ParagraphStyle(
        'MainTitleStyle',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=16,
        alignment=1, # Center
        spaceAfter=15,
    )
    elements.append(Paragraph("<u>STUDENT LIST</u>", title_style))

    subtitle_style = ParagraphStyle(
        'SubtitleStyle',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=11,
        alignment=1, # Centered with title
        spaceAfter=20,
        textColor=colors.darkgrey
    )
    subject_map = {
        "dpharm_2": "2ND YR D.PHARM",
        "bpharm_4": "2ND YR B.PHARM (SEM-IV)",
        "bpharm_5": "3RD YR B.PHARM (SEM-V)",
        "bpharm_6": "3RD YR B.PHARM (SEM-VI)"
    }
    subtitle = f"Subject: {subject_map.get(subject_code, 'All Subjects')}"
    elements.append(Paragraph(subtitle, subtitle_style))

    # --- Table Data ---
    data = [["Roll No", "Batch", "Student Name", "Email ID", "Mobile", "Status"]]
    for s in students:
        status = "Active" if s.is_active else "Inactive"
        data.append([
            s.roll_no or "---",
            s.assigned_batch_name,
            f"{s.first_name} {s.last_name}",
            s.email,
            s.mobile or "---",
            status
        ])

    table = Table(data, colWidths=[55, 75, 135, 135, 75, 50]) # Total width = 525 (fits in 535 available)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#ff4b2b")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Times-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTNAME', (0, 1), (-1, -1), 'Times-Roman'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#fff5f5")]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(table)

    # --- Page Setup (Border, Footer) ---
    def page_setup(canvas, doc):
        canvas.saveState()
        
        # --- Page Border ---
        canvas.setStrokeColor(colors.HexColor("#ff4b2b"))
        canvas.setLineWidth(1)
        canvas.rect(20, 20, A4[0]-40, A4[1]-40) # Standard page border
        
        # --- GMARS Logo and Footer ---
        try:
            gmars_logo_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'logo.png')
            if os.path.exists(gmars_logo_path):
                # Increased Height further
                canvas.drawImage(gmars_logo_path, A4[0] - 115, 1, width=85, height=90, mask='auto')
        except Exception:
            pass
        
        canvas.setFont('Times-Italic', 8)
        canvas.drawRightString(A4[0] - 120, 40, "powered by Gmars Tech Solutions")
        
        canvas.setFont('Times-Roman', 8)
        canvas.drawString(40, 40, f"Generated on: {now().strftime('%d-%m-%Y %H:%M')}")
        canvas.drawCentredString(A4[0]/2, 40, f"Page {canvas.getPageNumber()}")
        canvas.restoreState()

    try:
        doc.build(elements, onFirstPage=page_setup, onLaterPages=page_setup)
    except Exception as e:
        return HttpResponse(f"Error generating PDF: {str(e)}", status=500)
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Students_{subject_code or "All"}.pdf"'
    response.write(buffer.getvalue())
    buffer.close()
    return response


# =====================================================
# EXPORT STUDENTS → EXCEL (Formatted)
# =====================================================
def export_students_excel(request):
    if request.session.get("role") != "teacher":
        return redirect("/login/")

    subject_code = request.GET.get("subject")
    teacher = request.user

    students = User.objects.filter(
        role="student",
        created_by=teacher,
        college=teacher.college
    ).order_by("roll_no")

    if subject_code:
        students = students.filter(subject=subject_code)

    # Batch mapping logic
    batches = Batch.objects.filter(teacher=teacher)
    for student in students:
        student.assigned_batch_name = "---"
        if student.roll_no and student.roll_no.isdigit():
            roll_int = int(student.roll_no)
            for b in batches:
                if b.start_roll <= roll_int <= b.end_roll:
                    student.assigned_batch_name = b.name
                    break

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Students List"

    # Header Row
    headers = ["Roll No", "Batch", "Student Name", "Email ID", "Mobile No", "Status"]
    ws.append(headers)

    # Styling Header
    header_fill = PatternFill(start_color="FF4B2B", end_color="FF4B2B", fill_type="solid")
    header_font = Font(color="FFFFFF", bold=True)
    alignment = Alignment(horizontal="center", vertical="center")
    
    for cell in ws[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = alignment

    # Data Rows
    for s in students:
        ws.append([
            s.roll_no or "---",
            s.assigned_batch_name,
            f"{s.first_name} {s.last_name}",
            s.email,
            s.mobile or "---",
            "Active" if s.is_active else "Inactive"
        ])

    # Column Widths
    column_widths = [12, 15, 30, 35, 15, 12]
    for i, width in enumerate(column_widths):
        ws.column_dimensions[get_column_letter(i+1)].width = width

    buffer = io.BytesIO()
    wb.save(buffer)
    
    response = HttpResponse(
        buffer.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="Students_{subject_code or "All"}.xlsx"'
    return response


# =====================================================
# TEACHER → EXPERIMENTS LIST
# =====================================================
def teacher_experiments(request):
    if request.session.get("role") not in ["teacher", "superadmin"]:
        return redirect("/login/")

    experiments = Experiment.objects.filter(is_active=True).order_by("number")

    # 🔥 Plan-based filtering
    college = request.user.college
    if college and college.selected_plan == 'dpharm':
        experiments = experiments.filter(number__in=D_PHARM_NUMBERS)


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

    # Activate student and assign subject
    student = approval.student
    student.is_active = True
    student.subject = approval.requested_subject  # 🔥 NEW: Assign the requested subject
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

    experiments = Experiment.objects.filter(is_active=True).order_by("number")

    college = request.user.college
    if college and college.selected_plan == 'dpharm':
        experiments = experiments.filter(number__in=D_PHARM_NUMBERS)
    elif college and college.selected_plan == 'single':
        # Handle single experiment plan
        pass

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

    subject_code = request.GET.get("subject")
    
    exams = Exam.objects.filter(
        teacher=request.user
    )
    
    if subject_code:
        # Derive year from subject_code
        target_year = subject_code
        if subject_code in ["bpharm_5", "bpharm_6"]:
            target_year = "bpharm_56"
        exams = exams.filter(year=target_year)

    return render(
        request,
        "teacher/exams.html",
        {
            "exams": exams,
            "subject_code": subject_code
        }
    )

def teacher_create_exam(request):
    if request.session.get("role") != "teacher":
        return redirect("/login/")

    subject_code = request.GET.get("subject")

    if request.method == "POST":
        title = request.POST.get("title")
        exam_type = request.POST.get("exam_type")
        # year is now determined by subject context
        duration = request.POST.get("duration")

        # Derive year from subject_code
        # Mapping: dpharm_2 -> dpharm_2, bpharm_4 -> bpharm_4, bpharm_5/6 -> bpharm_56
        year = subject_code
        if subject_code in ["bpharm_5", "bpharm_6"]:
            year = "bpharm_56"

        if not all([title, exam_type, year, duration]):
            return redirect(f"/teacher/exams/?subject={subject_code or ''}")

        Exam.objects.create(
            teacher=request.user,
            title=title,
            exam_type=exam_type,
            year=year,
            duration_minutes=int(duration)
        )

        return redirect(f"/teacher/exams/?subject={subject_code or ''}")

    return render(request, "teacher/create_exam.html", {"subject_code": subject_code})

def teacher_edit_exam(request, exam_id):
    if request.session.get("role") != "teacher":
        return redirect("/login/")

    subject_code = request.GET.get("subject")

    exam = get_object_or_404(
        Exam,
        id=exam_id,
        teacher=request.user
    )

    if request.method == "POST":
        exam.title = request.POST.get("title")
        exam.exam_type = request.POST.get("exam_type")
        
        # Derived from subject context if provided, otherwise keep existing
        if subject_code:
            year = subject_code
            if subject_code in ["bpharm_5", "bpharm_6"]:
                year = "bpharm_56"
            exam.year = year
            
        exam.duration_minutes = int(request.POST.get("duration"))
        exam.save()

        return redirect(f"/teacher/exams/?subject={subject_code or ''}")

    return render(
        request,
        "teacher/edit_exam.html",
        {
            "exam": exam,
            "subject_code": subject_code
        }
    )

def teacher_toggle_exam(request, exam_id):
    if request.session.get("role") != "teacher":
        return redirect("/login/")

    subject_code = request.GET.get("subject")

    exam = get_object_or_404(
        Exam,
        id=exam_id,
        teacher=request.user
    )

    exam.is_active = not exam.is_active
    exam.save()

    return redirect(f"/teacher/exams/?subject={subject_code or ''}")

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

            bank_id = request.POST.get("bank_id")
            bank_item = get_object_or_404(SpottingBank, id=bank_id)

            ExamSpotting.objects.create(
                exam=exam,
                bank_item=bank_item,
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
            "spotting_bank": SpottingBank.objects.filter(is_active=True).order_by("name"),
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