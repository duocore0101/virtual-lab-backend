import os
import re

# Directory containing experiment templates
TEMPLATE_DIR = r"d:\virtual-lab-backend\templates\experiments"

# Persistent Scraper JavaScript for downloadPDF function
# This version saves the table data to localStorage so it can be retrieved on the conclusion page.
DOWNLOAD_PDF_JS = """
<script>
function downloadPDF() {
  const slug = "{{ experiment.slug }}";
  
  // 1. TRY TO SCRAPE TABLE DATA FROM DOM
  let tableData = [];
  const table = document.querySelector('table'); 
  if (table) {
    const rows = table.querySelectorAll('tr');
    rows.forEach(row => {
      let rowData = [];
      const cells = row.querySelectorAll('th, td');
      cells.forEach(cell => {
        rowData.push(cell.innerText.trim());
      });
      if (rowData.length > 0) rowData.push(""); // filler
      if (rowData.length > 0) tableData.push(rowData.filter(c => c !== ""));
    });
    
    // Save to localStorage for use on conclusion/other pages
    if (tableData.length > 0) {
        localStorage.setItem('exp_data_' + slug, JSON.stringify(tableData));
    }
  } 
  
  // 2. IF DOM TABLE IS MISSING/EMPTY, TRY LOCALSTORAGE
  if (tableData.length === 0) {
    const saved = localStorage.getItem('exp_data_' + slug);
    if (saved) {
        tableData = JSON.parse(saved);
    }
  }

  fetch(`/experiment/${slug}/download-pdf/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": "{{ csrf_token }}"
    },
    body: JSON.stringify({
      table_data: tableData
    })
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

# HTML for Download Button (Same)
DOWNLOAD_BUTTON_HTML = """
    <button class="exp-btn" onclick="downloadPDF()" style="background: linear-gradient(135deg, #10b981, #059669); box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);">
      Download Practical PDF 📄
    </button>
"""

def process_file(file_path):
    # We only care about files that have the downloadPDF function from previous run
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    if "function downloadPDF()" not in content:
        # Check if it HAS a finish button, maybe it was missed
        if 'onclick="finishPractical()"' not in content:
            return False
            
    # Update the script block
    # Regex to find the whole <script>block containing downloadPDF
    script_pattern = re.compile(r'<script>\s*function downloadPDF\(\)\s*\{.*?\}\s*</script>', re.IGNORECASE | re.DOTALL)
    
    if script_pattern.search(content):
        new_content = script_pattern.sub(DOWNLOAD_PDF_JS, content)
    else:
        # If it was missed but has finish button, add it
        finish_pattern = re.compile(r'(<button[^>]+onclick=["\']finishPractical\(\)["\'][^>]*>.*?Finish Practical.*?</button>)', re.IGNORECASE | re.DOTALL)
        if finish_pattern.search(content):
            new_content = finish_pattern.sub(lambda m: DOWNLOAD_BUTTON_HTML + "\n    " + m.group(1), content)
            if "</body>" in content:
                new_content = new_content.replace("</body>", DOWNLOAD_PDF_JS + "\n</body>")
            else:
                new_content += DOWNLOAD_PDF_JS
        else:
            return False

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return True

def run():
    count = 0
    for root, dirs, files in os.walk(TEMPLATE_DIR):
        for file in files:
            if file in ["experiment.html", "conclusion.html"]:
                file_path = os.path.join(root, file)
                if process_file(file_path):
                    count += 1
    print(f"Total files updated with Persistent Scraper: {count}")

if __name__ == "__main__":
    run()
