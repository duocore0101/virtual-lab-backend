import os
import sys
import django

# Add the current directory to sys.path
sys.path.append(os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from experiments.models import Experiment

try:
    exp = Experiment.objects.get(slug='diphenhydramine-asthma-guinea-pig')
    print(f"Current Name: {exp.name}")
    print(f"Current Aim: {exp.aim}")
    
    exp.name = "Effect of diphenhydramine in experimentally produced asthma in Rabbit"
    exp.aim = "To Study the Effect of Diphenhydramine in Experimentally Produced Asthma in Rabbit"
    exp.save()
    
    print("Updated Name and Aim successfully.")
except Experiment.DoesNotExist:
    print("Experiment with slug 'diphenhydramine-asthma-guinea-pig' not found.")
except Exception as e:
    print(f"Error: {e}")
