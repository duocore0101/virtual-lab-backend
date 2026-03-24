import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from experiments.models import Experiment

experiments = Experiment.objects.all().order_by('number')
for e in experiments:
    print(f"{e.number}: {e.name} ({e.slug})")
