import os

# Root directory for templates
TEMPLATE_ROOT = 'd:\\virtual-lab-backend\\templates\\experiments'

# Experiments to process (Slug, Back Page, Conclusion Text)
MISSING_EXP_DATA = [
    {
        'slug': 'introduction-to-pharmacology',
        'back': 'theory',
        'conclusion': 'Pharmacology is a vast and dynamic field that bridges basic sciences with clinical medicine. Understanding the foundational concepts of drug action, dosage, and side effects is essential for safe and effective therapeutic interventions.'
    },
    {
        'slug': 'experimental-instruments',
        'back': 'experiment',
        'conclusion': 'Familiarity with specialized instruments such as kymographs, organ baths, and rotarod is crucial for conducting precise pharmacological research. Proper handling and calibration of these tools ensure the reliability and reproducibility of experimental data.'
    },
    {
        'slug': 'common-laboratory-animals',
        'back': 'experiment',
        'conclusion': 'Different laboratory animals like mice, rats, rabbits, and guinea pigs offer unique advantages for specific pharmacological studies. Selecting the appropriate animal model is vital for accurately simulating human diseases and testing drug efficacy.'
    },
    {
        'slug': 'in-vitro-pharmacology-pss',
        'back': 'theory',
        'conclusion': 'Physiological salt solutions like Tyrode, Krebs, and Ringer are essential for maintaining the viability of isolated tissues in vitro. These solutions mimic the extracellular environment, allowing for the study of drug-receptor interactions in a controlled setting.'
    },
    {
        'slug': 'preclinical-types',
        'back': 'theory',
        'conclusion': 'Preclinical testing involves a combination of in vivo (in whole animals), in vitro (in isolated tissues), and ex vivo studies. This multi-tiered approach is fundamental for assessing the safety and efficacy of new drug candidates before clinical trials.'
    },
    {
        'slug': 'lab-animal-maintenance',
        'back': 'theory',
        'conclusion': 'Strict adherence to CPCSEA guidelines ensures the ethical treatment and optimal health of laboratory animals. Standardized maintenance conditions minimize external variables, leading to more consistent and scientifically valid experimental outcomes.'
    },
    {
        'slug': 'blood-withdrawal-techniques',
        'back': 'experiment',
        'conclusion': 'Proficiency in techniques like cardiac puncture, retro-orbital withdrawal, and tail snip is essential for obtaining high-quality blood samples. Proper separation of serum and plasma is equally important for various biochemical and pharmacological analyses.'
    },
    {
        'slug': 'routes-drug-administration',
        'back': 'experiment',
        'conclusion': "The route of administration (oral, IV, IM, IP, etc.) significantly influences a drug's absorption, distribution, and onset of action. Understanding these differences is critical for designing effective dosing regimens in experimental models."
    },
    {
        'slug': 'epm-anxiolytic-activity',
        'back': 'experiment',
        'conclusion': 'The elevated plus maze is a reliable behavioral model for assessing anxiolytic activity. Drugs that increase the time spent in open arms relative to closed arms are considered to have potential anti-anxiety properties.'
    },
    {
        'slug': 'bioassay-assembly',
        'back': 'theory',
        'conclusion': 'Proper assembly and stabilization of the bioassay setup are prerequisites for accurate quantitative assessment of active substances. Mastery of these technical skills is essential for performing reproducible bioassays on isolated tissues.'
    },
    {
        'slug': 'biostatistical-methods',
        'back': 'wilcoxon',
        'conclusion': 'Biostatistical tools such as t-tests, ANOVA, and Chi-square are indispensable for interpreting experimental data. These methods allow researchers to determine if observed differences are statistically significant, ensuring evidence-based conclusions.'
    }
]

TEMPLATE_CONTENT = """{{% load static %}}
<!DOCTYPE html>
<html lang="en">
<head>
  <script>(function(){{const t=localStorage.getItem('gmars-theme-preference');if(t==='light')document.body.classList.add('light-mode');}})();</script>
  <meta charset="UTF-8">
  <title>Result & Conclusion | Virtual Lab</title>

  <!-- Reuse existing CSS -->
  <link rel="stylesheet"
        href="{{% static 'experiments/rotarod/css/intro.css' %}}">

  <style>
    /* 🔝 TOP RIGHT ACTION BUTTONS */
    .top-actions {{
      position: fixed;
      top: 20px;
      right: 25px;
      display: flex;
      gap: 12px;
      z-index: 9999;
    }}

    .top-actions button {{
      padding: 10px 18px;
      border-radius: 22px;
      border: none;
      cursor: pointer;
      font-weight: 600;
      background: #ff2e2e;
      color: #fff;
      box-shadow: 0 0 14px rgba(255, 0, 0, 0.6);
      transition: transform 0.25s, box-shadow 0.25s;
    }}

    .top-actions button:hover {{
      transform: scale(1.08);
      box-shadow: 0 0 22px rgba(255, 0, 0, 0.9);
    }}
  </style>
</head>

<body>

<!-- 🔝 TOP RIGHT BUTTONS -->
<div class="top-actions">
  <button onclick="toggleTheme()">🌗 Theme</button>
  <button onclick="toggleFullscreen()">⛶ Full Screen</button>
</div>

<div class="page-container">

  <h1 class="title">Result & Conclusion</h1>

  <!-- 🧪 RESULT (General) -->
  <div class="info-box">
    <p>
      The experiment was conducted successfully following the standard protocols. 
      Observations were recorded and analyzed to determine the pharmacological outcome.
    </p>
  </div>

  <!-- 🧠 CONCLUSION -->
  <div class="info-box">
    <h2>Conclusion</h2>
    <p>
      {conclusion_text}
    </p>
  </div>

  <!-- 🔘 NAVIGATION -->
  <div class="button-row">

    <button class="back-btn" 
      onclick="location.href='/experiment/{{{{ experiment.slug }}}}/{back_page}/'">
      ⬅ Back
    </button>

    <button class="exp-btn" onclick="downloadPDF()" style="background: linear-gradient(135deg, #10b981, #059669); box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);">
      Download Practical PDF 📄
    </button>

    <button class="exp-btn" onclick="finishPractical()">
      Finish Practical ✔
    </button>

  </div>

</div>

<script>
function toggleFullscreen() {{
  if (!document.fullscreenElement) {{
    document.documentElement.requestFullscreen().catch(() => {{
      alert("Fullscreen not supported");
    }});
  }} else {{
    document.exitFullscreen();
  }}
}}
</script>

<script>
function downloadPDF() {{
  const slug = "{{{{ experiment.slug }}}}";
  let tableData = [];
  const saved = localStorage.getItem('exp_data_' + slug);
  if (saved) {{
      tableData = JSON.parse(saved);
  }}

  fetch(`/experiment/${{slug}}/download-pdf/`, {{
    method: "POST",
    headers: {{
      "Content-Type": "application/json",
      "X-CSRFToken": "{{{{ csrf_token }}}}"
    }},
    body: JSON.stringify({{
      table_data: tableData
    }})
  }})
  .then(res => {{
    if (!res.ok) throw new Error("PDF generation failed");
    return res.blob();
  }})
  .then(blob => {{
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `Practical_Report_${{slug}}.pdf`;
    document.body.appendChild(a);
    a.click();
    a.remove();
  }})
  .catch(err => {{
    alert("Failed to generate PDF");
    console.error(err);
  }});
}}

function finishPractical() {{
  fetch("/experiment/finish/", {{
    method: "POST",
    headers: {{
      "Content-Type": "application/json"
    }},
    body: JSON.stringify({{
      experiment_slug: "{{{{ experiment.slug }}}}",
      observations: {{
        status: "Completed"
      }}
    }})
  }})
  .then(res => res.json())
  .then(data => {{
    window.location.href = data.redirect;
  }})
  .catch(err => {{
    alert("Failed to submit practical");
    console.error(err);
  }});
}}
</script>

<script src="{{% static 'js/theme-toggle.js' %}}?v=20"></script>
</body>
</html>
"""

def generate_conclusions():
    for data in MISSING_EXP_DATA:
        slug = data['slug']
        back = data['back']
        text = data['conclusion']
        
        target_dir = os.path.join(TEMPLATE_ROOT, slug)
        target_file = os.path.join(target_dir, 'conclusion.html')
        
        if not os.path.exists(target_dir):
            print(f"Skipping {slug}: directory not found")
            continue
            
        content = TEMPLATE_CONTENT.format(
            conclusion_text=text,
            back_page=back
        )
        
        with open(target_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Created: {target_file}")

if __name__ == "__main__":
    generate_conclusions()
