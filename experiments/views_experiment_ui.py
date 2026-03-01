from django.shortcuts import render, get_object_or_404, redirect
from experiments.models import Experiment


# ==========================================
# ALLOWED PAGES
# ==========================================
ALLOWED_PAGES = ['intro', 'experiment', 'conclusion', 'instructions']


# ==========================================
# GENERIC EXPERIMENT PAGE (UI)
# ==========================================
def experiment_page(request, slug, page):

    # 🔥 ADDED: Role Protection (Student + Admin only)
    role = request.session.get("role")
    if role not in ["student","teacher", "admin"]:
        return redirect("/login/")

    # Validate page
    if page not in ALLOWED_PAGES:
        page = 'intro'

    # Get experiment
    experiment = get_object_or_404(
        Experiment,
        slug=slug,
        is_active=True
    )

    # Template path
    template_path = f"experiments/{experiment.experiment_type}/{page}.html"

    # Context
    context = {
        "experiment": experiment,

        # 🔥 Use session-based name (your project standard)
        "student": request.session.get("name"),

        # 🔥 Demo mode for admin
        "demo_mode": role == "admin",
    }

    return render(request, template_path, context)