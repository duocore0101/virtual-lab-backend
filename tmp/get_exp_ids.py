import os
import sys
import django

root_dir = r"d:\virtual-lab-backend"
sys.path.insert(0, root_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from experiments.models import Experiment

experiments = Experiment.objects.all().order_by('number')
with open(os.path.join(root_dir, 'tmp', 'exp_ids.txt'), 'w', encoding='utf-8') as f:
    for e in experiments:
        f.write(f"{e.id}|{e.number}|{e.slug}|{e.name}\n")
print("Done writing experiment IDs to tmp/exp_ids.txt")
