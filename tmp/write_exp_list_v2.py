import os
import sys
import django

# Add the project root to sys.path
root_dir = r"d:\virtual-lab-backend"
sys.path.insert(0, root_dir)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from experiments.models import Experiment

experiments = Experiment.objects.all().order_by('number')
with open(os.path.join(root_dir, 'tmp', 'exp_list.txt'), 'w', encoding='utf-8') as f:
    for e in experiments:
        f.write(f"{e.number}: {e.name} ({e.slug})\n")
print("Done writing experiment list to tmp/exp_list.txt")
