import os
import sys
import django

# Add the current directory to sys.path
sys.path.append(os.getcwd())

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from experiments.models import Experiment

e = Experiment.objects.filter(number=56).first()
with open("tmp/verify_final.txt", "w", encoding="utf-8") as f:
    if e:
        f.write(f"VERIFIED: {e.name}, Slug: {e.slug}, Number: {e.number}")
    else:
        f.write("NOT FOUND")
