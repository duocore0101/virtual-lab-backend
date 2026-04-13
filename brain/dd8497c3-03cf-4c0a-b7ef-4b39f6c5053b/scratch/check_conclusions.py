import os
import django
import sys

# Setup Django environment
sys.path.append('d:\\virtual-lab-backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from experiments.models import Experiment

def check_conclusions():
    experiments = Experiment.objects.all().order_by('number')
    template_root = 'd:\\virtual-lab-backend\\templates\\experiments'
    
    missing = []
    total_count = experiments.count()
    checked_count = 0
    
    for exp in experiments:
        slug = exp.slug
        conclusion_path = os.path.join(template_root, slug, 'conclusion.html')
        checked_count += 1
        
        if not os.path.exists(conclusion_path):
            missing.append({
                'number': exp.number,
                'name': exp.name,
                'slug': slug
            })
            
    print(f"Total Experiments: {total_count}")
    print(f"Checked: {checked_count}")
    print(f"Missing conclusion.html: {len(missing)}")
    print("\nList of experiments missing conclusion.html:")
    print("-" * 50)
    for index, item in enumerate(missing, 1):
        print(f"{index}. Exp #{item['number']}: {item['name']} (slug: {item['slug']})")

if __name__ == "__main__":
    check_conclusions()
