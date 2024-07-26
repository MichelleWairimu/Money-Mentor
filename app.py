import os
import pandas as pd
import streamlit as st
from ocr import extract_text_from_image, extract_text_from_pdf_image
import fitz  # PyMuPDF
import tempfile
import matplotlib.pyplot as plt
from fpdf import FPDF

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def extract_text_from_pdf(file_path):
    text = ""
    with fitz.open(file_path) as pdf:
        for page in pdf:
            text += page.get_text()
    if not text.strip():  # If no text found, try OCR
        text = extract_text_from_pdf_image(file_path)
    return text

def analyze_data(data):
    processed_data = data.describe()
    analysis_results = {
        'suggestions': "Improve marketing strategy.",
        'profit_before': data['profit'].sum(),
        'profit_after': data['profit'].sum() * 1.1  # Example increase
    }
    return processed_data, analysis_results

def analyze_text(text):
    processed_data = text
    analysis_results = {
        'suggestions': "Reduce operational costs.",
        'profit_before': 100000,  # Example value
        'profit_after': 110000  # Example increase
    }
    return processed_data, analysis_results

def generate_report(data, analysis):
    try:
        plt.switch_backend('Agg')

        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        pdf_path = temp_file.name

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Financial Analysis Report", ln=True, align='C')
        pdf.ln(10)
        pdf.multi_cell(0, 10, txt=str(data).encode('latin-1', 'replace').decode('latin-1'))
        pdf.ln(10)
        pdf.multi_cell(0, 10, txt="Suggestions: " + analysis['suggestions'].encode('latin-1', 'replace').decode('latin-1'))
        pdf.ln(10)
        pdf.cell(200, 10, txt=f"Profit Before: {analysis['profit_before']}", ln=True)
        pdf.cell(200, 10, txt=f"Profit After: {analysis['profit_after']}", ln=True)

        plt.figure()
        plt.bar(['Before', 'After'], [analysis['profit_before'], analysis['profit_after']])
        plt.xlabel('Scenario')
        plt.ylabel('Profit')
        plt.title('Profit Comparison')
        graph_path = tempfile.NamedTemporaryFile(delete=False, suffix='.png').name
        plt.savefig(graph_path)
        pdf.image(graph_path, x=10, y=None, w=100)

        pdf.output(pdf_path)
        return pdf_path
    except Exception as e:
        st.error(f"An error occurred while generating the report: {e}")
        raise

def main():
    st.title("Money Mentor")
    st.write("Upload your financial statements for analysis.")

    uploaded_file = st.file_uploader("Choose a file", type=['xls', 'csv', 'pdf', 'jpeg', 'png'])
    if uploaded_file is not None:
        file_path = os.path.join(UPLOAD_FOLDER, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.write(f"File uploaded: {uploaded_file.name}")

        try:
            if uploaded_file.name.endswith('.xls') or uploaded_file.name.endswith('.csv'):
                data = pd.read_excel(file_path) if uploaded_file.name.endswith('.xls') else pd.read_csv(file_path)
                processed_data, analysis_results = analyze_data(data)
                st.write("Data analyzed from .xls or .csv file")
            elif uploaded_file.name.endswith('.pdf'):
                text = extract_text_from_pdf(file_path)
                processed_data, analysis_results = analyze_text(text)
                st.write("Text extracted and analyzed from .pdf file")
            elif uploaded_file.name.endswith('.jpeg') or uploaded_file.name.endswith('.png'):
                text = extract_text_from_image(file_path)
                processed_data, analysis_results = analyze_text(text)
                st.write("Text extracted and analyzed from .jpeg or .png file")
            else:
                st.error("Unsupported file type")
                return

            report_path = generate_report(processed_data, analysis_results)
            st.write(f"Report generated: {report_path}")

            with open(report_path, "rb") as f:
                st.download_button("Download Report", f, file_name="report.pdf")
        
        except Exception as e:
            st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
