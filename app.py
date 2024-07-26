import os
from flask import Flask, render_template, request, redirect, url_for, send_file
import pandas as pd
from ocr import extract_text_from_image, extract_text_from_pdf_image
import fitz  # PyMuPDF
import tempfile

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        try:
            print("POST request received")
            print("Request files:", request.files)
            if 'file' not in request.files:
                print("No file part in request")
                return "No file part in request", 400

            file = request.files['file']
            if file.filename == '':
                print("No file selected")
                return "No file selected", 400

            if file:
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(file_path)
                print(f"File saved to {file_path}")

                # Process file based on its extension
                if file.filename.endswith('.xls') or file.filename.endswith('.csv'):
                    data = pd.read_excel(file_path) if file.filename.endswith('.xls') else pd.read_csv(file_path)
                    # Process data and generate analysis
                    processed_data, analysis_results = analyze_data(data)
                    print("Data analyzed from .xls or .csv file")
                elif file.filename.endswith('.pdf'):
                    text = extract_text_from_pdf(file_path)
                    processed_data, analysis_results = analyze_text(text)
                    print("Text extracted and analyzed from .pdf file")
                elif file.filename.endswith('.jpeg') or file.filename.endswith('.png'):
                    text = extract_text_from_image(file_path)
                    processed_data, analysis_results = analyze_text(text)
                    print("Text extracted and analyzed from .jpeg or .png file")
                else:
                    print("Unsupported file type")
                    return "Unsupported file type", 400

                # Generate report
                report_path = generate_report(processed_data, analysis_results)
                print(f"Report generated: {report_path}")
                return send_file(report_path, as_attachment=True)

            print("No file received")
        except Exception as e:
            print(f"An error occurred: {e}")
            return f"An error occurred: {e}", 500
    return render_template('upload_file.html')


def extract_text_from_pdf(file_path):
    text = ""
    with fitz.open(file_path) as pdf:
        for page in pdf:
            text += page.get_text()
    if not text.strip():  # If no text found, try OCR
        text = extract_text_from_pdf_image(file_path)
    return text

def analyze_data(data):
    # Analyze data and generate insights and graphs
    # Placeholder function: Replace with actual logic
    processed_data = data.describe()
    analysis_results = {
        'suggestions': "Improve marketing strategy.",
        'profit_before': data['profit'].sum(),
        'profit_after': data['profit'].sum() * 1.1  # Example increase
    }
    return processed_data, analysis_results

def analyze_text(text):
    # Placeholder function: Replace with actual logic
    processed_data = text
    analysis_results = {
        'suggestions': "Reduce operational costs.",
        'profit_before': 100000,  # Example value
        'profit_after': 110000  # Example increase
    }
    return processed_data, analysis_results

def generate_report(data, analysis):
    try:
        import matplotlib.pyplot as plt
        from fpdf import FPDF

        # Use 'Agg' backend to avoid GUI issues with Matplotlib
        plt.switch_backend('Agg')

        # Create a temporary PDF file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        pdf_path = temp_file.name
        print(f"Generating report at {pdf_path}")

        # Example report generation using FPDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        # Add content to PDF
        pdf.cell(200, 10, txt="Financial Analysis Report", ln=True, align='C')
        pdf.ln(10)
        pdf.multi_cell(0, 10, txt=str(data).encode('latin-1', 'replace').decode('latin-1'))
        pdf.ln(10)
        pdf.multi_cell(0, 10, txt="Suggestions: " + analysis['suggestions'].encode('latin-1', 'replace').decode('latin-1'))
        pdf.ln(10)
        pdf.cell(200, 10, txt=f"Profit Before: {analysis['profit_before']}", ln=True)
        pdf.cell(200, 10, txt=f"Profit After: {analysis['profit_after']}", ln=True)

        # Add example graph
        plt.figure()
        plt.bar(['Before', 'After'], [analysis['profit_before'], analysis['profit_after']])
        plt.xlabel('Scenario')
        plt.ylabel('Profit')
        plt.title('Profit Comparison')
        graph_path = tempfile.NamedTemporaryFile(delete=False, suffix='.png').name
        plt.savefig(graph_path)
        pdf.image(graph_path, x=10, y=None, w=100)

        # Save PDF
        pdf.output(pdf_path)
        print(f"Report successfully generated at {pdf_path}")
        return pdf_path
    except Exception as e:
        print(f"An error occurred while generating the report: {e}")
        raise

if __name__ == '__main__':
    app.run(debug=True)
