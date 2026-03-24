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
    print(f"ℹ️ Experiment #{exp_number} already exists.")
