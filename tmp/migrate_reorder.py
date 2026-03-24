import os
import sys
import django
from django.db import transaction

# Add the project root to sys.path
root_dir = r"d:\virtual-lab-backend"
sys.path.insert(0, root_dir)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from experiments.models import Experiment

def reorder_experiments():
    try:
        with transaction.atomic():
            # 1. Delete duplicate experiment #3 (ID 60)
            try:
                dup = Experiment.objects.get(id=60)
                print(f"Deleting duplicate experiment: {dup.name} (ID 60)")
                dup.delete()
            except Experiment.DoesNotExist:
                print("Duplicate experiment (ID 60) not found or already deleted.")

            # 2. Shift experiments 6-55 to 7-56
            # We use a temporary high offset to avoid number collisions during incrementing
            # if there were unique constraints (though we checked and there aren't, it's safer)
            
            exps_to_shift = Experiment.objects.filter(number__gte=6, number__lte=55).exclude(slug="preclinical-types").order_by('-number')
            print(f"Shifting {exps_to_shift.count()} experiments (Numbers 6-55) to 7-56")
            for exp in exps_to_shift:
                old_num = exp.number
                exp.number += 1
                exp.save()
                # print(f"  Shifted {exp.slug}: {old_num} -> {exp.number}")

            # 3. Move experiment 56 to 6
            try:
                exp_56 = Experiment.objects.get(slug="preclinical-types")
                print(f"Reordering {exp_56.name} from {exp_56.number} to 6")
                exp_56.number = 6
                exp_56.save()
            except Experiment.DoesNotExist:
                print("Experiment 'preclinical-types' not found.")

            print("Database migration completed successfully!")

    except Exception as e:
        print(f"Error during migration: {e}")
        transaction.set_rollback(True)

if __name__ == "__main__":
    reorder_experiments()
