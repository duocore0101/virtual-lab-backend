import os
import re

# Directory containing experiment templates
TEMPLATE_DIR = r"d:\virtual-lab-backend\templates\experiments"

# JavaScript for downloadPDF function
DOWNLOAD_PDF_JS = """
<script>
function downloadPDF() {
  const slug = "{{ experiment.slug }}";
  fetch(`/experiment/${slug}/download-pdf/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": "{{ csrf_token }}"
    }
  })
  .then(res => {
    if (!res.ok) throw new Error("PDF generation failed");
    return res.blob();
  })
  .then(blob => {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `Practical_Report_${slug}.pdf`;
    document.body.appendChild(a);
    a.click();
    a.remove();
  })
  .catch(err => {
    alert("Failed to generate PDF");
    console.error(err);
  });
}
</script>
"""

# HTML for Download Button
DOWNLOAD_BUTTON_HTML = """
    <button class="exp-btn" onclick="downloadPDF()" style="background: linear-gradient(135deg, #10b981, #059669); box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);">
      Download Practical PDF 📄
    </button>
"""

def process_file(file_path):
    print(f"Processing: {file_path}")
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Pattern to find the Finish Practical button
    finish_pattern = re.compile(r'(<button[^>]+onclick=["\']finishPractical\(\)["\'][^>]*>.*?Finish Practical.*?</button>)', re.IGNORECASE | re.DOTALL)
    
    if not finish_pattern.search(content):
        return False

    # 2. Check for existing PDF button and replace it if it's the old style
    # If it has downloadPDF() in onclick, we'll replace it.
    old_pdf_button_pattern = re.compile(r'<button[^>]+onclick=["\']downloadPDF\(\)["\'][^>]*>.*?</button>', re.IGNORECASE | re.DOTALL)
    if old_pdf_button_pattern.search(content):
        content = old_pdf_button_pattern.sub(DOWNLOAD_BUTTON_HTML, content)
        print(f"  - Replaced old PDF button.")
    else:
        # Insert button before the finish button
        content = finish_pattern.sub(lambda m: DOWNLOAD_BUTTON_HTML + "\n    " + m.group(1), content)
        print(f"  - Inserted new Download PDF button.")

    # 3. Check for existing downloadPDF script and replace it
    old_script_pattern = re.compile(r'<script>\s*function downloadPDF\(\)\s*\{.*?\}\s*</script>', re.IGNORECASE | re.DOTALL)
    if old_script_pattern.search(content):
        content = old_script_pattern.sub(DOWNLOAD_PDF_JS, content)
        print(f"  - Replaced old downloadPDF script.")
    else:
        # Append before </body> or at the end
        if "</body>" in content:
            content = content.replace("</body>", DOWNLOAD_PDF_JS + "\n</body>")
            print(f"  - Added new downloadPDF script.")
        else:
            content += DOWNLOAD_PDF_JS
            print(f"  - Appended new downloadPDF script.")

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True

def run():
    count = 0
    for root, dirs, files in os.walk(TEMPLATE_DIR):
        for file in files:
            if file in ["experiment.html", "conclusion.html"]:
                file_path = os.path.join(root, file)
                if process_file(file_path):
                    count += 1
    print(f"Total files updated: {count}")

if __name__ == "__main__":
    run()
