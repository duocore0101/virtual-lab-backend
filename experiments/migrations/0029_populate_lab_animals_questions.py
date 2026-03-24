from django.db import migrations

def populate_lab_animals(apps, schema_editor):
    Experiment = apps.get_model('experiments', 'Experiment')
    MCQBank = apps.get_model('experiments', 'MCQBank')
    ShortAnswerBank = apps.get_model('experiments', 'ShortAnswerBank')

    exp_title = "Study of common laboratory animals in experimental pharmacology"
    experiment, created = Experiment.objects.get_or_create(
        name=exp_title,
        defaults={
            'number': 3,
            'experiment_type': 'other',
            'aim': 'To study common laboratory animals used in experimental pharmacology.',
            'slug': 'lab-animals'
        }
    )

    mcqs = [
        {
            "text": "The most commonly used animal in experimental pharmacology for drug screening and toxicity studies is:",
            "a": "Guinea pig", "b": "Rabbit", "c": "Albino rat", "d": "Dog",
            "correct": "C"
        },
        {
            "text": "Which animal is preferably used for screening of analgesic drugs using the acetic acid writhing test?",
            "a": "Rat", "b": "Albino mouse", "c": "Guinea pig", "d": "Frog",
            "correct": "B"
        },
        {
            "text": "Guinea pig is the animal of choice for evaluation of:",
            "a": "Pyrogens", "b": "Bronchodilators and antihistamines", "c": "Anticonvulsants", "d": "Insulin",
            "correct": "B"
        },
        {
            "text": "Pyrogen testing in injectables is routinely performed using:",
            "a": "Mouse", "b": "Rat", "c": "Rabbit", "d": "Guinea pig",
            "correct": "C"
        },
        {
            "text": "The animal commonly used for recording blood pressure effects of autonomic drugs in anesthetized condition is:",
            "a": "Rat", "b": "Dog", "c": "Rabbit", "d": "Mouse",
            "correct": "B"
        },
        {
            "text": "Frog's rectus abdominis muscle preparation is used to study:",
            "a": "Skeletal muscle relaxants", "b": "Cardiac drugs", "c": "Antihypertensives", "d": "Antidiabetics",
            "correct": "A"
        }
    ]

    for m in mcqs:
        MCQBank.objects.create(
            question_text=m["text"],
            option_a=m["a"],
            option_b=m["b"],
            option_c=m["c"],
            option_d=m["d"],
            correct_option=m["correct"],
            experiment=experiment,
            is_active=True
        )

    shorts = [
        "1. Name the most commonly used animal in experimental pharmacology. Give reasons.",
        "2. Which animal is commonly used for screening analgesics and anticonvulsants? Mention two experimental models used for this purpose.",
        "3. Name the animal commonly used for evaluation of bronchodilators and antihistamines. Why is this animal preferred?",
        "4. Which animal is preferred for pyrogen testing? Give the reason for its use.",
        "5. List four commonly used animals in experimental pharmacology and mention one specific use for each."
    ]

    for s in shorts:
        ShortAnswerBank.objects.create(
            question_text=s,
            experiment=experiment,
            is_active=True
        )

class Migration(migrations.Migration):
    dependencies = [
        ('experiments', '0028_populate_instruments_questions'),
    ]
    operations = [
        migrations.RunPython(populate_lab_animals),
    ]
