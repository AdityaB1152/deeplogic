import PyPDF2
from pdf2image import convert_from_path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os
from django.conf import settings
from django.core.files.storage import default_storage
import cv2
import hashlib
from skimage.metrics import structural_similarity as ssim

def extract_text_from_pdf(pdf_path):
    try:
        pdf_file = open(pdf_path , 'rb')
        reader = PyPDF2.PdfReader(pdf_file)
        text=''
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text += page.extract_text()
        pdf_file.close()
        return text
    except Exception as e:
        raise Exception (f"Error Extracting the text from PDF: {str(e)}")
     


def convert_pdf_to_image(pdf_path):
    try:
        # Save the uploaded PDF to a temporary file
        temp_pdf_path = default_storage.path(pdf_path)
        images = convert_from_path(temp_pdf_path)
        if not images:
            raise Exception("No images found in PDF")
        
        # Save the first page as an image
        image_path = os.path.join(os.path.dirname(temp_pdf_path), f"{os.path.splitext(os.path.basename(temp_pdf_path))[0]}.png")
        images[0].save(image_path, 'PNG')
        return image_path
    except Exception as e:
        raise Exception(f"Error converting PDF to image: {str(e)}")
    

def calculate_text_similarity(text1 , text2):
    try:
        vectorizer = TfidfVectorizer().fit([text1 , text2])
        tfidf_matrix = vectorizer.transform([text1 , text2])
        cosine_sim = cosine_similarity(tfidf_matrix)[0,1]
        return cosine_sim
    except Exception as e:
        raise Exception(f"Error calculating text similarity: {str(e)}")
    


def calculate_structural_similarity(image_path1 , image_path2):
    try:
        image1 = cv2.imread(image_path1 , cv2.IMREAD_GRAYSCALE)
        image2 = cv2.imread(image_path2 , cv2.IMREAD_GRAYSCALE)
        score, _ = ssim(image1 , image2 , full=True)
    except Exception as e:
        raise Exception(f"Error calculating structural similarity: {str(e)}")
    
def calculate_combined_similarity(text_similarity , structural_similarity , text_weight=0.7, structure_weight=0.3):
    return (text_similarity * text_weight) + (structural_similarity * structure_weight)


def generate_file_hash(file_path):
    hash_alg = hashlib.sha256()  # Use SHA-256 for a unique hash
    try:
        with open(file_path, 'rb') as file:
            while chunk := file.read(8192):
                hash_alg.update(chunk)
        return hash_alg.hexdigest()
    except Exception as e:
        raise Exception(f"Error generating file hash: {str(e)}")