import os
import sys
import django

# Add the current directory to sys.path
sys.path.append(os.getcwd())

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from experiments.models import Experiment

exp_name = "Preclinical Experiments: Types and Details (In Vivo, In Vitro, Ex Vivo)"
exp_slug = "preclinical-types"
exp_number = 56

exp, created = Experiment.objects.get_or_create(
    number=exp_number,
    defaults={
        "name": exp_name,
        "slug": exp_slug,
        "experiment_type": "other",
        "aim": "To understand different types of preclinical experiments including In Vivo, In Vitro, and Ex Vivo models.",
        "description": "Detailed overview of preclinical experimental methodologies.",
        "order": exp_number
    }
)

if created:
    print(f"✅ Successfully created experiment #{exp_number}: {exp_name}")
else:
    # If exists, update name and slug in case they were different
    exp.name = exp_name
    exp.slug = exp_slug
    exp.save()
    print(f"ℹ️ Experiment #{exp_number} updated.")
