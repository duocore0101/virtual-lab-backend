import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from experiments.models import MCQBank, ShortAnswerBank, Experiment

# 1. Clear existing banks
print("Clearing existing banks...")
MCQBank.objects.all().delete()
ShortAnswerBank.objects.all().delete()

# 2. Find or create the experiment
exp_title = "Introduction to Pharmacology, Experimental Pharmacology, its Scope, Objectives, and Foundational Concepts"
experiment, created = Experiment.objects.get_or_create(
    name=exp_title,
    defaults={'number': 1, 'experiment_type': 'other', 'aim': 'To understand the foundational concepts of Pharmacology.'}
)

if created:
    print(f"Created experiment: {exp_title}")
else:
    print(f"Found experiment: {exp_title}")

# 3. Add MCQs
mcqs = [
    {
        "text": "The term “Pharmacology” is derived from Greek words “Pharmakon” and “Logos” meaning:",
        "a": "Drug + Study", "b": "Poison + Medicine", "c": "Treatment + Disease", "d": "Body + Drug",
        "correct": "A"
    },
    {
        "text": "“Medicine” differs from “Drug” because it contains:",
        "a": "Only active ingredient", "b": "Drug + excipients", "c": "Only excipients", "d": "Only therapeutic agents",
        "correct": "B"
    },
    {
        "text": "Pharmacokinetics (PK) is the study of:",
        "a": "What the drug does to the body", "b": "What the body does to the drug", "c": "Mechanism of action", "d": "Toxicity only",
        "correct": "B"
    },
    {
        "text": "One of the main objectives of Experimental Pharmacology is:",
        "a": "To perform clinical trials directly", "b": "To support preclinical development before clinical trials", "c": "To market the drug", "d": "To conduct Phase IV only",
        "correct": "B"
    },
    {
        "text": "Preclinical studies are mainly conducted to generate data for:",
        "a": "NDA", "b": "IND application to CDSCO", "c": "Phase IV", "d": "Post-marketing surveillance",
        "correct": "B"
    },
    {
        "text": "The stage where Experimental Pharmacology plays the major role in the drug development pipeline is:",
        "a": "Target Identification", "b": "Preclinical Studies", "c": "Phase III", "d": "Regulatory Review",
        "correct": "B"
    },
    {
        "text": "“Replacement” in 4Rs principle means:",
        "a": "Using fewer animals", "b": "Using alternatives like simulation software", "c": "Minimizing pain", "d": "Rehabilitating animals",
        "correct": "B"
    },
    {
        "text": "Bioavailability is a parameter of:",
        "a": "Pharmacodynamics", "b": "Pharmacokinetics", "c": "Pharmacovigilance", "d": "Bioassay",
        "correct": "B"
    },
    {
        "text": "NDA is submitted to CDSCO after successful completion of:",
        "a": "Preclinical studies", "b": "Phase III clinical trials", "c": "Phase I", "d": "Target identification",
        "correct": "B"
    },
    {
        "text": "As per PCI guidelines, live animal experiments in pharmacy practicals are replaced by:",
        "a": "Only theory lectures", "b": "Simulated software / virtual labs", "c": "Human volunteers", "d": "Chemical assays only",
        "correct": "B"
    }
]

print("Adding MCQs...")
for m in mcqs:
    MCQBank.objects.create(
        question_text=m["text"],
        option_a=m["a"],
        option_b=m["b"],
        option_c=m["c"],
        option_d=m["d"],
        correct_option=m["correct"],
        experiment=experiment,
        is_active=True
    )

# 4. Add Short Answers
shorts = [
    {"text": "Differentiate between Pharmacology and Experimental Pharmacology."},
    {"text": "Define ‘Drug’ and ‘Medicine’. How do they differ?"},
    {"text": "Explain Pharmacokinetics (PK) and Pharmacodynamics (PD) with one example each."},
    {"text": "List the five main aims/objectives of Experimental Pharmacology."},
    {"text": "Why are Preclinical studies conducted? Give any four reasons."},
    {"text": "Describe the role of Experimental Pharmacology in the Drug Discovery and Development Pipeline."},
    {"text": "Explain the 4Rs principle in animal experimentation."},
    {"text": "What is IND and NDA? In which stages are they submitted?"},
    {"text": "Write a short note on Bioavailability."},
    {"text": "Explain the importance of simulation software in Experimental Pharmacology as per PCI guidelines."}
]

print("Adding Short Answers...")
for s in shorts:
    ShortAnswerBank.objects.create(
        question_text=s["text"],
        experiment=experiment,
        is_active=True
    )

print("Finished populating question bank.")
