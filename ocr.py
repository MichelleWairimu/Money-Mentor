from google.cloud import vision
from google.oauth2 import service_account
from PIL import Image
import io

# Path to your Google Cloud service account key file
SERVICE_ACCOUNT_PATH = r"moneymentor-430519-153e7f808079.json"

# Initialize Google Cloud Vision client
credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_PATH)
client = vision.ImageAnnotatorClient(credentials=credentials)

def extract_text_from_image(image_path):
    """Extract text from an image using Google Cloud Vision."""
    try:
        print(f"Extracting text from image: {image_path}")
        with io.open(image_path, 'rb') as image_file:
            content = image_file.read()
        
        image = vision.Image(content=content)
        response = client.text_detection(image=image)
        texts = response.text_annotations
        text = texts[0].description if texts else ""
        print("Text successfully extracted.")
        return text
    except Exception as e:
        print(f"An error occurred: {e}")
        return ""

def extract_text_from_pdf_image(pdf_path):
    """Extract text from an image in a PDF using Google Cloud Vision."""
    import fitz  # PyMuPDF

    text = ""
    with fitz.open(pdf_path) as pdf:
        for page_number in range(len(pdf)):
            page = pdf.load_page(page_number)
            pix = page.get_pixmap()
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            img_path = 'temp_image.png'
            img.save(img_path)

            text += extract_text_from_image(img_path)
    
    return text


if __name__ == "__main__":
    # Test extracting text from an image
    image_text = extract_text_from_image("Screenshot.png")
    print("Extracted Text from Image:", image_text)
    
    # Test extracting text from a PDF
    pdf_text = extract_text_from_pdf_image("BSTDB Financial Statements for 2021.pdf")
    print("Extracted Text from PDF:", pdf_text)
