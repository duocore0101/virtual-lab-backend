# ================================
# REST API VIEWS (UNCHANGED)
# ================================
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from datetime import date
import json

# 🔥 ADDED: Import MCQ & Short models (SAFE)
from .models import (
    Experiment,
    ExperimentAttempt,
    Observation,
)

from .serializers import ExperimentSerializer


# -------------------------
# API: LIST ALL EXPERIMENTS
# -------------------------
class ExperimentListView(ListAPIView):
    queryset = Experiment.objects.filter(is_active=True)
    serializer_class = ExperimentSerializer
    permission_classes = [IsAuthenticated]


# -------------------------
# API: SINGLE EXPERIMENT
# -------------------------
class ExperimentDetailView(RetrieveAPIView):
    queryset = Experiment.objects.filter(is_active=True)
    serializer_class = ExperimentSerializer
    lookup_field = 'slug'
    permission_classes = [IsAuthenticated]


# ================================
# UI: GENERIC EXPERIMENT PAGE VIEW
# ================================

ALLOWED_PAGES = [
    "intro",
    "theory",
    "requirements",
    "experiment",
    "experiment2",
    "graph",
    "conclusion",

    "swiss-albino-mice",
    "wistar-rat",
    "sprague-dawley-rat",
    "long-evans-rat",
    "guinea-pig",
    "hamsters",
    "frogs",
    "dog",
    "cat",

    "student-organ-bath",
    "sherrington-kymograph",
    "actophotometer",
    "rotarod",
    "hot-plate",
    "digital-telethermometer",
    "pole-climbing",
    "staircase",
    "y-maze",
    "elevated-plus-maze",
    "open-field",
    "hole-board",
    "electroconvulsiometer",
    "plethysmometer",
    "tail-flick",
    "langendorff",
    "basic-surgical-instruments",

    'cardiac-puncture',
    'posterior-vena-cava',
    'marginal-ear-vein',
    'tarsal-vein',
    'retro-orbital-sinus',
    'tail-vein',
    'dorsal-pedal-vein',
    'tail-snip',

    # 🔥 NEW ROUTE PAGES
    "oral-gavage",
    "intraperitoneal",
    "subcutaneous",
    "dermal-topical",
    "ocular-topical",
    "intramuscular",
    "intravenous",

]


def experiment_page(request, slug, page):

    # 🔥 UPDATED: Allow Admin Demo Mode
    role = request.session.get("role")

    if role not in ["student","teacher", "admin"]:
        return redirect("/login/")

    if page not in ALLOWED_PAGES:
        page = "intro"

    experiment = get_object_or_404(
        Experiment,
        slug=slug,
        is_active=True
    )

    template_path = f"experiments/{slug}/{page}.html"

    return render(
        request,
        template_path,
        {
            "experiment": experiment,
            "student": request.session.get("name"),
            "demo_mode": role == "admin",  # 🔥 SAFE ADDITION
        }
    )


# =====================================================
# PRACTICAL: FINISH PRACTICAL (SAVE STUDENT DATA)
# =====================================================
@csrf_exempt
def finish_practical(request):

    if request.method != "POST":
        return JsonResponse({"error": "Invalid method"}, status=405)

    role = request.session.get("role")

    # 🔥 UPDATED: Allow admin but do not save
    if role not in ["student","teacher", "admin"]:
        return JsonResponse({"error": "Unauthorized"}, status=401)

    try:
        data = json.loads(request.body.decode("utf-8"))
    except Exception:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    experiment_slug = data.get("experiment_slug")
    observations = data.get("observations", {})
    roll_no = data.get("roll_no")  # 🔥 SAFE ADDITION (optional future use)

    experiment = get_object_or_404(
        Experiment,
        slug=experiment_slug,
        is_active=True
    )

    # 🔥 ADMIN DEMO MODE (NO DATABASE SAVE)
    if role == "admin":
        return JsonResponse({
            "status": "success",
            "redirect": f"/experiment/{experiment.slug}/"
        })

    # ================= ORIGINAL STUDENT LOGIC BELOW =================

    attempt = ExperimentAttempt.objects.create(
        student=request.user,
        experiment=experiment,
        completed_at=now()
    )

    # 🔥 SAFE (OPTIONAL FUTURE STORAGE LOGIC)
    # If later you add roll_no field in model,
    # you can attach it here without breaking anything.

    for param, value in observations.items():
        Observation.objects.create(
            attempt=attempt,
            parameter=param,
            value=value
        )

    return JsonResponse({
        "status": "success",
        "redirect": "/student/dashboard/"
    })


# =========================================
# PDF: AUTO-GENERATE ROTAROD PRACTICAL PDF
# =========================================
@csrf_exempt
def generate_rotarod_pdf(request, slug):

    if request.method != "POST":
        return HttpResponse("Method not allowed", status=405)

    role = request.session.get("role")

    # 🔥 UPDATED: Allow admin demo
    if role not in ["student","teacher","admin"]:
        return HttpResponse("Unauthorized", status=401)

    try:
        data = json.loads(request.body.decode("utf-8"))
    except Exception:
        return HttpResponse("Invalid JSON", status=400)

    pre = data.get("pre", [])
    post = data.get("post", [])
    roll_no = data.get("roll_no")  # 🔥 SAFE ADDITION
    student = request.session.get("name", "Student")

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = (
        'attachment; filename="Rotarod_Practical_Report.pdf"'
    )

    pdf = canvas.Canvas(response, pagesize=A4)
    width, height = A4
    y = height - 50

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawCentredString(width / 2, y, "G-MARS Virtual Pharmacology Lab")
    y -= 25

    pdf.setFont("Helvetica", 12)
    pdf.drawCentredString(width / 2, y, "Rotarod Experiment – Practical Journal")
    y -= 25

    # 🔥 SAFE ADDITION: Show Roll No if available
    if roll_no:
        pdf.drawCentredString(width / 2, y, f"Roll No: {roll_no}")
        y -= 20

    pdf.drawCentredString(width / 2, y, f"Student: {student}")
    y -= 40

    pdf.showPage()
    pdf.save()

    return response

