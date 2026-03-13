from experiments.models import StudentApproval

def teacher_context(request):
    """
    Provides global context for the teacher dashboard, 
    including subject lists and pending request counts.
    """
    if not request.user.is_authenticated or request.user.role != "teacher":
        return {}

    # 1. Subject List
    # We map codes to display names for the sidebar dropdown
    subject_map = {
        "dpharm_2": "2ND YR D.PHARM",
        "bpharm_4": "2ND YR B.PHARM (SEM-IV)",
        "bpharm_5": "3RD YR B.PHARM (SEM-V)",
        "bpharm_6": "3RD YR B.PHARM (SEM-VI)"
    }
    
    codes = request.user.subject.split(",") if request.user.subject else []
    teacher_subjects = []
    for code in codes:
        code = code.strip()
        if code:
            teacher_subjects.append({
                "code": code,
                "name": subject_map.get(code, code.upper())
            })

    # 2. Pending Requests Count
    pending_count = StudentApproval.objects.filter(
        selected_teacher=request.user,
        approval_status="pending"
    ).count()

    return {
        "teacher_subjects": teacher_subjects,
        "pending_student_requests_count": pending_count
    }
