import os
import sys
import django

root_dir = r"d:\virtual-lab-backend"
sys.path.insert(0, root_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from experiments.models import Experiment

print(f"Total experiments: {Experiment.objects.count()}")

try:
    p = Experiment.objects.get(slug='preclinical-types')
    print(f"preclinical-types: number={p.number}, id={p.id}")
except Exception as e:
    print(f"Error finding preclinical-types: {e}")

try:
    d = Experiment.objects.get(id=60)
    print(f"ID 60 found: {d.name}, number={d.number}")
except Exception as e:
    print(f"ID 60 NOT found: {e}")

exps_6_to_55 = Experiment.objects.filter(number__gte=6, number__lte=55).exclude(slug='preclinical-types')
print(f"Experiments between 6 and 55 (excluding preclinical): {exps_6_to_55.count()}")
for e in exps_6_to_55[:5]:
    print(f"  {e.number}: {e.slug}")
