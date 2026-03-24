import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from experiments.models import Experiment

experiments = Experiment.objects.all().order_by('number')
with open('d:\\virtual-lab-backend\\tmp\\exp_list.txt', 'w', encoding='utf-8') as f:
    for e in experiments:
        f.write(f"{e.number}: {e.name} ({e.slug})\n")
