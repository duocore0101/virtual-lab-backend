from django.urls import path

# =========================
# STUDENT UI VIEWS
# =========================
from .views_ui import (
    student_dashboard,
    experiment_intro,
    experiment_run,
    student_exam_dashboard,
    start_exam,
    submit_exam,
    student_view_result,
)

# =========================
# SUPER ADMIN VIEWS
# =========================
from .views_superadmin_ui import (
    # Dashboard & Create
    superadmin_dashboard,
    create_admin,
    # 🔥 PRINCIPAL APPROVAL SYSTEM
    superadmin_principal_requests,
    approve_principal_request,
    reject_principal_request,
    superadmin_college_detail,
    superadmin_teacher_detail,
    # Clickable card pages
    superadmin_colleges,
    superadmin_admins,
    superadmin_teachers,
    superadmin_students,
    superadmin_experiments,
    superadmin_attempts,

    # 🔹 SUPER ADMIN MODULES
    superadmin_reports,
    superadmin_billing,
    superadmin_cms,
    superadmin_support,
    superadmin_settings,
    superadmin_audit_logs,

    # ACTIVE / DEACTIVE ACTIONS
    superadmin_toggle_user,
    superadmin_toggle_college,
    superadmin_delete_college,
)

# =========================
# ADMIN VIEWS
# =========================
from .views_admin_ui import (
    # Dashboard
    admin_dashboard,
    admin_teacher_requests,
    reject_teacher_request,
    approve_teacher_request,
    # CRUD
    create_teacher,
    teacher_detail_admin,

    # Clickable card pages
    admin_teachers,
    admin_students,
    admin_experiments,
    admin_attempts,

    # 🔥 NEW ADMIN MODULES
    admin_reports,
    admin_audit_logs,

    # Activate / Deactivate
    admin_toggle_user,

    # CSV EXPORTS
    admin_export_students_csv,
    admin_export_attempts_csv,
)

# =========================
# TEACHER VIEWS
# =========================
from .views_teacher_ui import teacher_exam_builder
from .views_teacher_ui import (
    teacher_dashboard,
    create_student,
    reject_student_request,
    approve_student_request,
    teacher_student_requests,
    # Teacher clickable pages
    teacher_students,
    teacher_experiments,
    teacher_attempts,
    # 🔥 NEW BATCH MANAGEMENT
    teacher_manage_batches,
    teacher_create_batch,
    teacher_edit_batch,
    teacher_assign_practical,

    teacher_exams,
    teacher_create_exam,
    teacher_edit_exam,
    teacher_toggle_exam,
    delete_exam_mcq,
    delete_exam_short,
    delete_exam_spotting,
    teacher_exam_attempts,
    evaluate_attempt,
    export_students_pdf,
    export_students_excel,
)

# =========================
# EXPERIMENT / PRACTICAL VIEWS
# =========================
from .views import (
    experiment_page,
    generate_rotarod_pdf,
    finish_practical,
)


urlpatterns = [

    # =================================================
    # SUPER ADMIN (GLOBAL SAAS CONTROL)
    # =================================================
    path(
        "superadmin/dashboard/",
        superadmin_dashboard,
        name="superadmin-dashboard"
    ),
    path(
        "superadmin/create-admin/",
        create_admin,
        name="create-admin"
    ),

    path(
        "superadmin/colleges/",
        superadmin_colleges,
        name="superadmin-colleges"
    ),
    path(
        "superadmin/admins/",
        superadmin_admins,
        name="superadmin-admins"
    ),
    path(
        "superadmin/teachers/",
        superadmin_teachers,
        name="superadmin-teachers"
    ),
    path(
        "superadmin/students/",
        superadmin_students,
        name="superadmin-students"
    ),
    path(
        "superadmin/experiments/",
        superadmin_experiments,
        name="superadmin-experiments"
    ),
    path(
        "superadmin/attempts/",
        superadmin_attempts,
        name="superadmin-attempts"
    ),

    # =========================
    # SUPER ADMIN – EXTRA MODULES
    # =========================
    path(
        "superadmin/reports/",
        superadmin_reports,
        name="superadmin-reports"
    ),
    path(
        "superadmin/billing/",
        superadmin_billing,
        name="superadmin-billing"
    ),
    path(
        "superadmin/cms/",
        superadmin_cms,
        name="superadmin-cms"
    ),
    path(
        "superadmin/support/",
        superadmin_support,
        name="superadmin-support"
    ),
    path(
        "superadmin/settings/",
        superadmin_settings,
        name="superadmin-settings"
    ),
    path(
        "superadmin/audit-logs/",
        superadmin_audit_logs,
        name="superadmin-audit-logs"
    ),

    # =========================
    # SUPER ADMIN – ACTIONS
    # =========================
    path(
        "superadmin/toggle-user/<int:user_id>/",
        superadmin_toggle_user,
        name="superadmin-toggle-user"
    ),
    path(
        "superadmin/toggle-college/<int:college_id>/",
        superadmin_toggle_college,
        name="superadmin-toggle-college"
    ),
    path(
        "superadmin/delete-college/<int:college_id>/",
        superadmin_delete_college,
        name="superadmin-delete-college"
    ),

        # =================================================
    # 🔥 SUPER ADMIN – DRILL DOWN (COLLEGE → TEACHER → STUDENTS)
    # =================================================
    path(
        "superadmin/college/<int:college_id>/",
        superadmin_college_detail,
        name="superadmin-college-detail"
    ),

    path(
        "superadmin/teacher/<int:teacher_id>/",
        superadmin_teacher_detail,
        name="superadmin-teacher-detail"
    ),

        # =================================================
    # 🔥 SUPER ADMIN – PRINCIPAL APPROVAL SYSTEM
    # =================================================
    path(
        "superadmin/principal-requests/",
        superadmin_principal_requests,
        name="superadmin-principal-requests"
    ),

    path(
        "superadmin/principal-requests/approve/<int:request_id>/",
        approve_principal_request,
        name="approve-principal-request"
    ),

    path(
        "superadmin/principal-requests/reject/<int:request_id>/",
        reject_principal_request,
        name="reject-principal-request"
    ),

    
    

    # =================================================
    # DASHBOARDS
    # =================================================
    path(
        "student/dashboard/",
        student_dashboard,
        name="student-dashboard"
    ),
    path(
    "student/exams/",
    student_exam_dashboard,
    name="student-exams"
),
path(
    "student/exams/<int:exam_id>/start/",
    start_exam,
    name="start-exam"
),
path(
    "student/exams/<int:exam_id>/submit/",
    submit_exam,
    name="submit-exam"
),  
path(
    "student/exams/<int:exam_id>/result/",
    student_view_result,
    name="student-view-result"
),
    path(
        "admin/dashboard/",
        admin_dashboard,
        name="admin-dashboard"
    ),
    path(
        "teacher/dashboard/",
        teacher_dashboard,
        name="teacher-dashboard"
    ),

    # =================================================
    # ADMIN MODULES
    # =================================================
    path(
        "admin/reports/",
        admin_reports,
        name="admin-reports"
    ),
    path(
        "admin/audit-logs/",
        admin_audit_logs,
        name="admin-audit-logs"
    ),

    # =================================================
    # ADMIN ACTIONS
    # =================================================
    path(
        "admin/create-teacher/",
        create_teacher,
        name="create-teacher"
    ),
    path(
        "admin/teacher/<int:teacher_id>/",
        teacher_detail_admin,
        name="admin-teacher-detail"
    ),

    path(
        "admin/teachers/",
        admin_teachers,
        name="admin-teachers"
    ),
    path(
        "admin/students/",
        admin_students,
        name="admin-students"
    ),
    path(
        "admin/experiments/",
        admin_experiments,
        name="admin-experiments"
    ),
    path(
        "admin/attempts/",
        admin_attempts,
        name="admin-attempts"
    ),

    path(
        "admin/toggle-user/<int:user_id>/",
        admin_toggle_user,
        name="admin-toggle-user"
    ),

    path(
        "admin/export/students/",
        admin_export_students_csv,
        name="admin-export-students"
    ),
    path(
        "admin/export/attempts/",
        admin_export_attempts_csv,
        name="admin-export-attempts"
    ),

    path(
    "admin/teacher-requests/",
    admin_teacher_requests,
    name="admin-teacher-requests"
),

path(
    "admin/teacher-requests/approve/<int:request_id>/",
    approve_teacher_request,
    name="approve-teacher-request"
),

path(
    "admin/teacher-requests/reject/<int:request_id>/",
    reject_teacher_request,
    name="reject-teacher-request"
),

    # =================================================
    # TEACHER CLICKABLE CARDS
    # =================================================
    path(
        "teacher/students/",
        teacher_students,
        name="teacher-students"
    ),
    path(
        "teacher/experiments/",
        teacher_experiments,
        name="teacher-experiments"
    ),
    path(
        "teacher/attempts/",
        teacher_attempts,
        name="teacher-attempts"
    ),
    path(
        "teacher/export-students-pdf/",
        export_students_pdf,
        name="teacher-export-students-pdf"
    ),
    path(
        "teacher/export-students-excel/",
        export_students_excel,
        name="teacher-export-students-excel"
    ),

    path(
        "teacher/create-student/",
        create_student,
        name="create-student"
    ),
    # =================================================
    # 🔥 TEACHER → BATCH MANAGEMENT
    # =================================================
    path(
        "teacher/manage-batches/",
        teacher_manage_batches,
        name="teacher-manage-batches"
    ),

    path(
        "teacher/create-batch/",
        teacher_create_batch,
        name="teacher-create-batch"
    ),

    path(
        "teacher/batch/<int:batch_id>/edit/",
        teacher_edit_batch,
        name="teacher-edit-batch"
    ),

    path(
        "teacher/batch/<int:batch_id>/assign/",
        teacher_assign_practical,
        name="teacher-assign-practical"
    ),
    path(
    "teacher/student-requests/",
    teacher_student_requests,
    name="teacher-student-requests"
),

path(
    "teacher/student-requests/approve/<int:student_id>/",
    approve_student_request,
    name="approve-student-request"
),

path(
    "teacher/student-requests/reject/<int:student_id>/",
    reject_student_request,
    name="reject-student-request"
),
path(
    "teacher/attempt/<int:attempt_id>/evaluate/",
    evaluate_attempt,
    name="evaluate-attempt"
),


# =================================================
# 🔥 TEACHER → EXAM MANAGEMENT (PHASE 1)
# =================================================

path(
    "teacher/exams/",
    teacher_exams,
    name="teacher-exams"
),

path(
    "teacher/exams/create/",
    teacher_create_exam,
    name="teacher-create-exam"
),

path(
    "teacher/exams/<int:exam_id>/edit/",
    teacher_edit_exam,
    name="teacher-edit-exam"
),

path(
    "teacher/exams/<int:exam_id>/toggle/",
    teacher_toggle_exam,
    name="teacher-toggle-exam"
),
path(
    "teacher/exams/<int:exam_id>/builder/",
    teacher_exam_builder,
    name="teacher-exam-builder"
),
path(
    "teacher/mcq/delete/<int:mcq_id>/",
    delete_exam_mcq,
    name="delete-exam-mcq"
),
path(
    "teacher/short/delete/<int:short_id>/",
    delete_exam_short,
    name="delete-exam-short"
),
path(
    "teacher/spotting/delete/<int:spot_id>/",
    delete_exam_spotting,
    name="delete-exam-spotting"
),
path(
    "teacher/exams/<int:exam_id>/attempts/",
    teacher_exam_attempts,
    name="teacher-exam-attempts"
),
    # =================================================
    # PRACTICALS (⚠ ORDER IS CRITICAL)
    # =================================================
    path(
        "experiment/finish/",
        finish_practical,
        name="finish-practical"
    ),

    path(
        "experiment/<slug:slug>/download-pdf/",
        generate_rotarod_pdf,
        name="download-pdf"
    ),

    path(
        "experiment/<slug:slug>/run/",
        experiment_run,
        name="experiment-run"
    ),

    # ✅ INTRO ROUTE (MOVED ABOVE GENERIC PAGE)
    path(
        "experiment/<slug:slug>/",
        experiment_intro,
        name="experiment-intro"
    ),

    # ✅ GENERIC PAGE (LAST)
    path(
        "experiment/<slug:slug>/<str:page>/",
        experiment_page,
        name="experiment-page"
    ),
    
]
