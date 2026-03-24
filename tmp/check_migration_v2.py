import os
import sys
import django

root_dir = r"d:\virtual-lab-backend"
sys.path.insert(0, root_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from experiments.models import Experiment

output_path = os.path.join(root_dir, 'tmp', 'migrate_diag.txt')
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(f"Total experiments: {Experiment.objects.count()}\n")

    try:
        p = Experiment.objects.get(slug='preclinical-types')
        f.write(f"preclinical-types: number={p.number}, id={p.id}\n")
    except Exception as e:
        f.write(f"Error finding preclinical-types: {e}\n")

    try:
        d = Experiment.objects.get(id=60)
        f.write(f"ID 60 found: {d.name}, number={d.number}\n")
    except Exception as e:
        f.write(f"ID 60 NOT found: {e}\n")

    exps_6_to_55 = Experiment.objects.filter(number__gte=6, number__lte=55).exclude(slug='preclinical-types').order_by('number')
    f.write(f"Experiments between 6 and 55 (excluding preclinical): {exps_6_to_55.count()}\n")
    for e in exps_6_to_55:
        f.write(f"  {e.number}: {e.slug} (ID={e.id})\n")
