import PyPDF2
from pdf2image import convert_from_path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os
from django.conf import settings
import cv2
import hashlib
from skimage.metrics import structural_similarity as ssim

def extract_text_from_pdf(pdf_path):
    try:
        pdf_file = open(pdf_path , 'rb')
        reader = PyPDF2.PdfFileReader(pdf_file)
        text=''
        for page_num in range(reader.numPages):
            page = reader.getPage(page_num)
            text += page.extract_text()
        pdf_file.close()
        return text
    except Exception as e:
        raise Exception (f"Error Extracting the text from PDF: {str(e)}")
     


def convert_pdf_to_image(pdf_path):
    try:
        images = convert_from_path(pdf_path)
        image_path = os.path.join(settings.MEDIA_ROOT, 'invoices' , os.path.basename(pdf_path)+'.jpg')
        images[0].save(image_path , 'JPEG')
        return image_path
    except Exception as e:
        raise Exception(f"Error Converting PDF to image: {str(e)}")
    

def calculate_text_similarity(text1 , text2):
    try:
        vectorizer = TfidfVectorizer().fit([text1 , text2])
        tfidf_matrix = vectorizer.transform([text1 , text2])
        cosine_sim = cosine_similarity(tfidf_matrix)[0,1]
        return cosine_sim
    except Exception as e:
        raise Exception(f"Error calculating text similarity: {str(e)}")
    


def calculate_structral_similarity(image_path1 , image_path2):
    try:
        image1 = cv2.imread(image_path1 , cv2.IMREAD_GRAYSCALE)
        image2 = cv2.imread(image_path2 , cv2.IMREAD_GRAYSCALE)
        score, _ = ssim(image1 , image2 , full=True)
    except Exception as e:
        raise Exception(f"Error calculating structural similarity: {str(e)}")
    
def calculate_combined_similarity(text_similarity , structural_similarity , text_weight=0.7, structure_weight=0.3):
    return (text_similarity * text_weight) + (structural_similarity * structure_weight)

def generate_file_hash(file_path):
    try:
        hasher = hashlib.sha256()
        with open(file_path , 'rb') as f:
            buf = f.read()
            hasher.update(buf)
        return hasher.hexdigest()
    except Exception as e:
         raise Exception(f"Error generating file hash: {str(e)}") 