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
import io
import os
import re
from django.utils.text import slugify
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, HRFlowable, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from django.conf import settings
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# =========================================
# 🔠 FONT REGISTRATION (CAMBRIA)
# =========================================
try:
    # Cambria Regular (Index 0 in ttc)
    font_path = "C:/Windows/Fonts/cambria.ttc"
    if os.path.exists(font_path):
        pdfmetrics.registerFont(TTFont('Cambria', font_path))
    
    # Cambria Bold
    bold_path = "C:/Windows/Fonts/cambriab.ttf"
    if os.path.exists(bold_path):
        pdfmetrics.registerFont(TTFont('Cambria-Bold', bold_path))

    # Cambria Italic
    italic_path = "C:/Windows/Fonts/cambriai.ttf"
    if os.path.exists(italic_path):
        pdfmetrics.registerFont(TTFont('Cambria-Italic', italic_path))

except Exception as e:
    print(f"Font registration failed: {e}")

# 🔥 ADDED: Import MCQ & Short models (SAFE)
from .models import (
    Experiment,
    ExperimentAttempt,
    Observation,
    Batch,
)

from .serializers import ExperimentSerializer
from .experiment_tables import EXPERIMENT_TABLES

D_PHARM_NUMBERS = [1, 2, 3, 6, 8, 9, 10, 11, 16, 17, 20, 21, 24, 25, 26, 27, 30, 31, 33, 36]


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
    'serum-plasma',
    'anaesthesia-euthanasia',

    # 🔥 NEW ROUTE PAGES
    "oral-gavage",
    "intraperitoneal",
    "subcutaneous",
    "dermal-topical",
    "ocular-topical",
    "intramuscular",
    "intravenous",

    # 🔥 NEW ROUTE
        "anova",
        "t-test",
        "chi-square",
        "wilcoxon",
        "in-vitro",
        "ex-vivo",
        "in-vivo",
    ]


def experiment_page(request, slug, page):

    # 🔥 UPDATED: Allow Admin Demo Mode
    role = request.session.get("role")

    if role not in ["student","teacher", "admin", "superadmin"]:
        return redirect("/login/")

    if page not in ALLOWED_PAGES:
        page = "intro"

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
                return redirect("/login/") # Or a restricted access page
        elif college and college.selected_plan == 'single':
            # Handle single experiment plan
            pass

    template_path = f"experiments/{slug}/{page}.html"

    # 🔥 SAFE ADDITION: Discover 3D model for preloading
    cached_model_path = None
    models_dir = os.path.join(settings.BASE_DIR, 'static', 'experiments', slug, 'models')
    if os.path.exists(models_dir):
        # Look for the first .glb file
        glb_files = [f for f in os.listdir(models_dir) if f.endswith('.glb')]
        if glb_files:
            cached_model_path = f"experiments/{slug}/models/{glb_files[0]}"

    return render(
        request,
        template_path,
        {
            "experiment": experiment,
            "student": request.session.get("name"),
            "demo_mode": role in ["admin", "superadmin"],  # 🔥 SAFE ADDITION
            "cached_model_path": cached_model_path,         # 🔥 Preloading support
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
    if role not in ["student","teacher", "admin", "superadmin"]:
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

    # 🔥 UPDATED DEMO MODE: Admin, Superadmin, and Teachers (NO DATABASE SAVE)
    if role in ["admin", "superadmin", "teacher"]:
        redirect_urls = {
            "admin": "/admin/experiments/",
            "superadmin": "/superadmin/experiments/",
            "teacher": "/teacher/experiments/"
        }
        return JsonResponse({
            "status": "success",
            "redirect": redirect_urls.get(role, "/login/")
        })

    # ================= ORIGINAL STUDENT LOGIC BELOW =================

    attempt = ExperimentAttempt.objects.create(
        student=request.user,
        experiment=experiment,
        completed_at=now()
    )

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
# HELPERS: PDF CONTENT EXTRACTION
# =========================================
def parse_html_table(html_str):
    """Extremely basic HTML table to list-of-lists parser."""
    rows = []
    # Identify all table rows
    tr_matches = re.finditer(r'<tr>(.*?)</tr>', html_str, flags=re.DOTALL | re.IGNORECASE)
    for tr in tr_matches:
        row_content = tr.group(1)
        # Find all th or td tags in the row
        cells = re.findall(r'<(th|td)[^>]*>(.*?)</\1>', row_content, flags=re.DOTALL | re.IGNORECASE)
        # Strip internal tags from each cell result
        row_data = [strip_tags(c[1]).strip() for c in cells]
        if row_data:
            rows.append(row_data)
    return rows

def get_template_text(template_name, context):
    """Renders a template and returns stripped text, removing UI noise."""
    try:
        html = render_to_string(template_name, context)
        # Remove head, script, style, and navigation buttons
        html = re.sub(r'<(head|script|style).*?>.*?</\1>', '', html, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove common button/ui text using regex (more aggressive)
        noise_patterns = [
            r'🌗\s*Theme', r'🌗\s*Toggle Theme', r'⛶\s*Full\s*Screen', 
            r'Slide\s*\d+\s*/\s*\d+', r'Slide\s*\d+', r'Back\s*▶', r'◀\s*Back', 
            r'Next\s*▶', r'◀\s*Next', r'Finish\s*Practical\s*✔',
            r'View\s*Observations\s*📊', r'Download\s*Practical\s*PDF\s*📄',
            r'⬅\s*Back', r'Next\s*▶', r'✔\s*Finish', r'🌗', r'⛶',
            r'\(?\s*\d+\s*/\s*\d+\s*\)?'
        ]
        for pattern in noise_patterns:
            html = re.sub(pattern, '', html, flags=re.IGNORECASE)

        # Extract ALL info-boxes (especially for multi-slide theories)
        info_boxes = re.findall(r'<div class="info-box[^"]*">(.*?)</div>', html, flags=re.DOTALL | re.IGNORECASE)
        if info_boxes:
            html = "\n\n".join(info_boxes)
            
        text = strip_tags(html)
        # Clean up whitespace and excessive newlines
        text = re.sub(r'\n\s*\n', '\n\n', text).strip()
        # Remove single words that are likely leftovers like "Back", "Next"
        text = re.sub(r'\b(Back|Next|Theme)\b', '', text)
        return text.strip()
    except:
        return ""

# =========================================
# PDF: GENERIC PRACTICAL REPORT PDF
# =========================================
@csrf_exempt
def generate_experiment_pdf(request, slug):

    if request.method != "POST":
        return HttpResponse("Method not allowed", status=405)

    role = request.session.get("role")
    if role not in ["student", "teacher", "admin", "superadmin"]:
        return HttpResponse("Unauthorized", status=401)

    experiment = get_object_or_404(Experiment, slug=slug, is_active=True)
    user = request.user
    
    # Load JSON data (Table observations)
    try:
        post_data = json.loads(request.body.decode("utf-8"))
    except:
        post_data = {}

    obs_table = post_data.get("table_data", []) # Expected: list of lists
    
    # 🌟 NEW: Fetch live data from database if POST data is missing/incomplete
    if (not obs_table or len(obs_table) < 2) and role == "student":
        try:
            latest_attempt = ExperimentAttempt.objects.filter(
                student=user, 
                experiment=experiment
            ).order_by('-completed_at').first()
            
            if latest_attempt:
                observations = Observation.objects.filter(attempt=latest_attempt)
                if observations.exists():
                    # Map observation values by parameter (cell ID)
                    obs_map = {str(o.parameter): o.value for o in observations}
                    
                    # Fetch template HTML and reconstruct table
                    html_table = EXPERIMENT_TABLES.get(slug, "")
                    if html_table:
                        # Find all cells in the HTML and map values
                        def replacer(match):
                            nonlocal cell_idx
                            cell_idx += 1
                            val = obs_map.get(str(cell_idx), "")
                            return f"<td>{val}</td>"
                        
                        cell_idx = 0
                        # Temporary reconstruction to use parse_html_table
                        filled_html = re.sub(r'<td>\s*</td>', replacer, html_table)
                        obs_table = parse_html_table(filled_html)
        except Exception:
            pass

    # Fallback to default table structure if data is still missing
    if not obs_table or len(obs_table) < 2:
        default_html = EXPERIMENT_TABLES.get(slug, "")
        if default_html:
            obs_table = parse_html_table(default_html)
    
    # Fetch college (Superadmin might not have one)
    college = user.college if role != "superadmin" else None

    # Student Info
    batch_name = "---"
    academic_year = f"{now().year}-{str(now().year + 1)[2:]}" # Default e.g. 2025-26
    student_class = "---"

    if role == "student":
        # Class Mapping
        subject_map = {
            'dpharm_2': 'Second Year D.Pharm',
            'bpharm_4': 'Second Year B.Pharm (Sem-IV)',
            'bpharm_5': 'Third Year B.Pharm (Sem-V)',
            'bpharm_6': 'Third Year B.Pharm (Sem-VI)',
        }
        student_class = subject_map.get(user.subject, user.subject or "---")
        
        # Batch Lookup
        if user.roll_no and user.roll_no.isdigit():
            try:
                rno = int(user.roll_no)
                batch = Batch.objects.filter(
                    teacher=user.created_by,
                    start_roll__lte=rno,
                    end_roll__gte=rno
                ).first()
                if batch:
                    batch_name = batch.name
            except:
                pass

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=A4, 
        rightMargin=30, 
        leftMargin=30, 
        topMargin=30, 
        bottomMargin=50
    )
    elements = []
    styles = getSampleStyleSheet()

    # --- Header (Branding) ---
    college_name = college.name if college else "G-MARS Virtual Lab System"
    college_address = college.address if college and college.address else ""
    
    logo_path = None
    if college and college.logo:
        try:
            if os.path.exists(college.logo.path):
                logo_path = college.logo.path
        except: pass

    name_style = ParagraphStyle('CN', parent=styles['Normal'], fontName='Cambria-Bold', fontSize=22, alignment=0, leading=24, textColor=colors.HexColor("#1e3a8a"))
    addr_style = ParagraphStyle('AD', parent=styles['Normal'], fontName='Cambria', fontSize=10, textColor=colors.grey, alignment=0)
    
    h_info = [Paragraph(college_name.upper(), name_style)]
    if college_address:
        h_info.append(Paragraph(college_address, addr_style))
    
    # Custom Detail Styles
    header_detail_style = ParagraphStyle('HDS', parent=styles['Normal'], fontName='Cambria', fontSize=10, leading=14)

    role_title = role.replace("superadmin", "Super Admin").title()

    if role == "student":
        h_info.append(Spacer(1, 5))
        h_info.append(Paragraph(f"<b>Student:</b> {user.first_name} {user.last_name} | <b>Roll No:</b> {user.roll_no or '---'}", header_detail_style))
        h_info.append(Paragraph(f"<b>Class:</b> {student_class} | <b>Batch:</b> {batch_name}", header_detail_style))
        h_info.append(Paragraph(f"<b>Academic Year:</b> {academic_year}", header_detail_style))
    else:
        h_info.append(Spacer(1, 5))
        h_info.append(Paragraph(f"<b>{role_title}:</b> {user.first_name} {user.last_name}", header_detail_style))

    if logo_path:
        logo_img = Image(logo_path, width=70, height=70)
        header_table = Table([[logo_img, h_info]], colWidths=[85, 455])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
        ]))
        elements.append(header_table)
    else:
        elements.extend(h_info)

    elements.append(Spacer(1, 10))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#1e3a8a"), spaceAfter=10))

    # --- PDF Metadata (Who downloaded) ---
    meta_style = ParagraphStyle('META', parent=styles['Normal'], fontName='Cambria-Italic', fontSize=9, textColor=colors.darkslategray, alignment=2)
    elements.append(Paragraph(f"PDF Generated By: {user.get_full_name()} ({role_title}) on {now().strftime('%d %b %Y, %I:%M %p')}", meta_style))
    elements.append(Spacer(1, 15))

    # --- Content ---
    report_title_style = ParagraphStyle(
        'RTS', 
        parent=styles['Normal'], 
        fontName='Cambria-Bold', 
        fontSize=14, 
        alignment=1, 
        spaceAfter=15,
        textColor=colors.HexColor("#111827"),
        leading=18
    )
    elements.append(Paragraph(f'<font color="#b91c1c">PRACTICAL REPORT:</font> {experiment.name.upper()}', report_title_style))
    elements.append(HRFlowable(width="60%", thickness=0.5, color=colors.grey, spaceAfter=20))

    # --- Content Sections ---
    section_title_style = ParagraphStyle('STS', parent=styles['Normal'], fontName='Cambria-Bold', fontSize=14, spaceAfter=10, textColor=colors.HexColor("#b91c1c"), borderPadding=2, borderLeftWidth=3, borderLeftColor=colors.HexColor("#b91c1c"))
    text_style = ParagraphStyle('TS', parent=styles['Normal'], fontName='Cambria', fontSize=12, leading=16, spaceAfter=15, alignment=4) # alignment 4 is JUSITFY

    # Context for template rendering
    ctx = {"experiment": experiment, "user": user}

    # 1. AIM
    elements.append(Paragraph("AIM", section_title_style))
    aim_text = get_template_text(f"experiments/{slug}/intro.html", ctx)
    elements.append(Paragraph(aim_text or experiment.aim or "As described in the experiment protocol.", text_style))

    # 2. REQUIREMENTS
    req_text = get_template_text(f"experiments/{slug}/requirements.html", ctx)
    if req_text:
        elements.append(Paragraph("REQUIREMENTS", section_title_style))
        elements.append(Paragraph(req_text, text_style))

    # 3. THEORY
    theory_text = get_template_text(f"experiments/{slug}/theory.html", ctx)
    if theory_text:
        elements.append(Paragraph("THEORY", section_title_style))
        elements.append(Paragraph(theory_text, text_style))

    # 4. OBSERVATION TABLE
    if obs_table:
        elements.append(PageBreak())
        elements.append(Paragraph("OBSERVATION TABLE", section_title_style))
        
        # Convert all cells to Paragraphs for wrapping
        table_content = []
        for row in obs_table:
            table_row = [Paragraph(str(cell), styles['Normal']) for cell in row]
            table_content.append(table_row)

        if table_content:
            t = Table(table_content, hAlign='LEFT', colWidths=[(A4[0]-60)/len(obs_table[0])] * len(obs_table[0]))
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f3f4f6")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor("#111827")),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Cambria-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Cambria'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ]))
            elements.append(t)
            elements.append(Spacer(1, 15))

    # 5. CONCLUSION
    conclusion_text = get_template_text(f"experiments/{slug}/conclusion.html", ctx)
    if conclusion_text:
        # If it was on page 2, and conclusion is short, it might be fine.
        # But let's ensure heading
        elements.append(Paragraph("CONCLUSION", section_title_style))
        elements.append(Paragraph(conclusion_text, text_style))

    def page_setup(canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor("#1e3a8a"))
        canvas.setLineWidth(1)
        canvas.rect(20, 20, A4[0]-40, A4[1]-40)
        
        # G-MARS Footer Logo
        try:
            gmars_logo = os.path.join(settings.BASE_DIR, 'static', 'images', 'logo.png')
            if os.path.exists(gmars_logo):
                canvas.drawImage(gmars_logo, A4[0] - 100, 15, width=60, height=60, mask='auto')
        except: pass
        
        canvas.setFont('Cambria-Bold', 11)
        canvas.drawRightString(A4[0] - 100, 50, "Signature of Examiner")
        
        canvas.setFont('Cambria', 9)
        canvas.drawString(40, 35, f"Report generated on: {now().strftime('%d-%m-%Y at %H:%M')}")
        canvas.drawCentredString(A4[0]/2, 35, f"Page {canvas.getPageNumber()}")
        canvas.restoreState()

    try:
        doc.build(elements, onFirstPage=page_setup, onLaterPages=page_setup)
    except Exception as e:
        return HttpResponse(f"Error: {str(e)}", status=500)
    
    response = HttpResponse(content_type='application/pdf')
    filename = f"Practical_Report_{slugify(experiment.name)}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    response.write(buffer.getvalue())
    buffer.close()
    return response

