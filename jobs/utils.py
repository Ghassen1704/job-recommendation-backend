import spacy
import pdfplumber

nlp = spacy.load("en_core_web_sm")

def extract_text_from_pdf(pdf_path):
    """Extracts text from a resume PDF"""
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text.strip()

def extract_skills(text):
    """Extract skills from resume using NLP"""
    doc = nlp(text)
    skills = [token.text for token in doc.ents if token.label_ in ["SKILL", "EDUCATION", "EXPERIENCE"]]
    return ", ".join(skills)


def extract_experience(text):
    """Extract experience from resume using NLP"""
    doc = nlp(text)
    experience = [token.text for token in doc.ents if token.label_ == "EXPERIENCE"]
    return ", ".join(experience)