from django.db import migrations

def populate_instruments(apps, schema_editor):
    Experiment = apps.get_model('experiments', 'Experiment')
    MCQBank = apps.get_model('experiments', 'MCQBank')
    ShortAnswerBank = apps.get_model('experiments', 'ShortAnswerBank')

    exp_title = "Study of Commonly Used Instruments in Experimental Pharmacology"
    experiment, created = Experiment.objects.get_or_create(
        name=exp_title,
        defaults={
            'number': 2,
            'experiment_type': 'other',
            'aim': 'To study commonly used instruments in experimental pharmacology.',
            'slug': 'common-instruments'
        }
    )

    mcqs = [
        {"text": "Sherrington's rotating drum is primarily used for:", "a": "Measuring locomotor activity", "b": "Recording tissue contractions", "c": "Inducing convulsions", "d": "Measuring paw volume", "correct": "B"},
        {"text": "The traditional recording medium on Sherrington's rotating drum is:", "a": "Digital sensor", "b": "Smoked paper", "c": "Infrared beams", "d": "Water displacement", "correct": "B"},
        {"text": "Student organ bath is used for:", "a": "In vivo behavioral studies", "b": "Isolated tissue experiments", "c": "Pyrogen testing", "d": "Locomotor measurement", "correct": "B"},
        {"text": "Tissue viability in organ bath is maintained by:", "a": "Electric shock", "b": "Carbogen aeration and 37°C temperature", "c": "Radiant heat", "d": "Paw immersion", "correct": "B"},
        {"text": "Actophotometer operates on the principle of:", "a": "Water displacement", "b": "Photocell beam interruptions", "c": "Thermal stimulus", "d": "Electroshock", "correct": "B"},
        {"text": "Actophotometer is used to screen:", "a": "Anti-inflammatory drugs", "b": "CNS stimulants/depressants", "c": "Anticonvulsants", "d": "Cardioactive drugs", "correct": "B"},
        {"text": "Plethysmometer measures:", "a": "Body temperature", "b": "Paw volume/edema", "c": "Heart rate", "d": "Head dips", "correct": "B"},
        {"text": "The common experimental model associated with plethysmometer is:", "a": "Maximal electroshock", "b": "Carrageenan-induced paw edema", "c": "Spontaneous alternation", "d": "Conditioned avoidance", "correct": "B"},
        {"text": "The standard temperature setting for Eddy’s hot plate analgesiometer is:", "a": "37°C", "b": "55°C", "c": "150 mA shock", "d": "Room temperature", "correct": "B"},
        {"text": "Eddy’s hot plate test primarily detects:", "a": "Peripheral analgesics", "b": "Centrally acting analgesics", "c": "Antihistaminics", "d": "Muscle relaxants", "correct": "B"},
        {"text": "In the tail flick analgesiometer test, the stimulus used is:", "a": "Electric shock", "b": "Radiant heat", "c": "Aerosol histamine", "d": "Hot water immersion", "correct": "B"},
        {"text": "Tail flick test measures:", "a": "Spinal reflex latency", "b": "Open arm exploration", "c": "Hindlimb extension", "d": "Coronary flow", "correct": "A"},
        {"text": "The main application of a telethermometer is:", "a": "Edema measurement", "b": "Pyrogen testing (fever response)", "c": "Anxiety screening", "d": "Convulsion induction", "correct": "B"},
        {"text": "The animal commonly used with a telethermometer for pyrogen testing is:", "a": "Mouse", "b": "Rabbit", "c": "Guinea pig", "d": "Frog", "correct": "B"},
        {"text": "Histamine aerosol chamber is used for screening:", "a": "Anticonvulsants", "b": "Antihistaminic drugs", "c": "Nootropics", "d": "Cardioactive drugs", "correct": "B"},
        {"text": "The endpoint observed in guinea pigs in histamine aerosol chamber is:", "a": "Tail flick", "b": "Pre-convulsive dyspnoea", "c": "Paw licking", "d": "Hindlimb extension", "correct": "B"},
        {"text": "Pole climbing apparatus tests:", "a": "Conditioned avoidance response", "b": "Spatial memory", "c": "Motor coordination", "d": "Exploratory head dips", "correct": "A"},
        {"text": "Selective blockade in pole climbing test indicates:", "a": "Sedative effect", "b": "Antipsychotic activity", "c": "Analgesic effect", "d": "Anti-inflammatory activity", "correct": "B"},
        {"text": "Electroconvulsiometer induces:", "a": "Paw edema", "b": "Maximal electroshock seizures", "c": "Anxiety", "d": "Bradycardia", "correct": "B"},
        {"text": "The protection endpoint for anticonvulsant activity in electroconvulsiometer test is:", "a": "Increased head dips", "b": "Abolition of hindlimb tonic extension", "c": "Open arm entries", "d": "Paw volume reduction", "correct": "B"},
        {"text": "Langendorff apparatus is used for:", "a": "Behavioral anxiety tests", "b": "Isolated perfused heart studies", "c": "Locomotor activity", "d": "Pain threshold", "correct": "B"},
        {"text": "The perfusion type used in Langendorff apparatus is:", "a": "Antegrade", "b": "Retrograde (aortic)", "c": "Subplantar", "d": "Aerosol", "correct": "B"},
        {"text": "Rotating rod (Rota-rod) apparatus assesses:", "a": "Memory", "b": "Motor coordination and balance", "c": "Inflammation", "d": "Convulsions", "correct": "B"},
        {"text": "Decreased fall latency in rota-rod indicates:", "a": "Anxiolytic effect", "b": "Muscle relaxation or CNS depression", "c": "Anticonvulsant effect", "d": "Stimulant effect", "correct": "B"},
        {"text": "The primary test performed using the Y-maze apparatus is:", "a": "Conditioned avoidance", "b": "Spontaneous alternation", "c": "Hot plate pain test", "d": "Edema measurement", "correct": "B"},
        {"text": "Y-maze is used to evaluate:", "a": "Anxiety", "b": "Spatial working memory", "c": "Motor grip strength", "d": "Bronchospasm", "correct": "B"},
        {"text": "Elevated plus maze is considered the gold standard for screening:", "a": "Nootropics", "b": "Anxiolytics and anxiogenics", "c": "Antihistaminics", "d": "Cardioactive drugs", "correct": "B"},
        {"text": "Anxiolytic drugs in elevated plus maze increase:", "a": "Hindlimb extension", "b": "Open arm time or entries", "c": "Paw volume", "d": "Convulsion duration", "correct": "B"},
        {"text": "Open field test measures:", "a": "Isolated heart function", "b": "Locomotion and anxiety", "c": "Tail flick latency", "d": "Pyrogen response", "correct": "B"},
        {"text": "The anxiety indicator in the open field test is:", "a": "Increased center exploration", "b": "Thigmotaxis (peripheral preference)", "c": "Head dips", "d": "Pole climbing", "correct": "B"},
        {"text": "In the staircase apparatus, the key parameters recorded are:", "a": "Paw volume and temperature", "b": "Steps climbed and rearings", "c": "Arm entries and alternation", "d": "Coronary flow and rate", "correct": "B"},
        {"text": "Anxiolytics in staircase apparatus typically:", "a": "Decrease both parameters", "b": "Selectively decrease rearings", "c": "Increase convulsions", "d": "Abolish extension", "correct": "B"},
        {"text": "Hole board apparatus primarily measures:", "a": "Tail flick", "b": "Head dipping (exploration)", "c": "Hindlimb extension", "d": "Open arm entries", "correct": "B"},
        {"text": "The effect of anxiolytics in hole board apparatus is:", "a": "Decrease head dips", "b": "Increase head dips", "c": "Induce edema", "d": "Block escape response", "correct": "B"}
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
        "1. What is the primary function of Sherrington’s rotating drum? Name one key accessory used with this instrument.",
        "2. For what type of experiments is the student organ bath used? How is tissue viability maintained in the organ bath?",
        "3. What parameter is measured using an actophotometer? Give one example of a drug effect that can be observed using this instrument.",
        "4. What does a plethysmometer measure in experimental pharmacology? Name the common inflammatory model used with this instrument.",
        "5. What is the typical endpoint response observed in Eddy’s hot plate analgesiometer test? Which type of analgesics is this method most sensitive to?",
        "6. What type of stimulus is applied in the tail flick test? Which class of analgesics shows a strong response in this test?",
        "7. What is the primary application of a telethermometer in pharmacological studies? Which animal model is commonly used with this instrument?",
        "8. The histamine aerosol chamber is used for screening which class of drugs? What is the key endpoint observed in guinea pigs?",
        "9. What type of behavioral response is tested using the pole climbing apparatus? This test is selective for which class of drugs?",
        "10. What type of seizure model is induced using an electroconvulsiometer? What is the key endpoint used to evaluate anticonvulsant activity?",
        "11. The Langendorff apparatus is used to study which physiological function? What type of perfusion mode is used in this technique?",
        "12. What parameter is measured using the rotating rod (rota-rod) apparatus? This test is sensitive to which type of drug effects?",
        "13. What type of test is performed using the Y-maze apparatus? Which cognitive function is assessed using this test?",
        "14. The elevated plus maze is based on which behavioral conflict? What effect do anxiolytic drugs produce in this test?",
        "15. What parameters are measured in the open field test? Which parameter indicates anxiety levels?",
        "16. What are the key parameters recorded in the staircase test? What effect do anxiolytic drugs have on rearing behavior?",
        "17. What type of exploratory behavior is measured using the hole board apparatus? What effect do anxiolytic drugs produce in this test?"
    ]

    for s in shorts:
        ShortAnswerBank.objects.create(
            question_text=s,
            experiment=experiment,
            is_active=True
        )

class Migration(migrations.Migration):
    dependencies = [
        ('experiments', '0027_populate_pharmacology_questions'),
    ]
    operations = [
        migrations.RunPython(populate_instruments),
    ]
