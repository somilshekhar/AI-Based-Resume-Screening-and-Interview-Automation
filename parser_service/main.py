
from fastapi import FastAPI, UploadFile, File, HTTPException
import pdfplumber, docx2txt, pytesseract, tempfile, os, io, json
from PIL import Image
import re
import spacy

nlp = spacy.load('en_core_web_sm')
app = FastAPI(title='Parser Service', version='0.1.0')

email_re = re.compile(r'[\w\.-]+@[\w\.-]+', re.I)
phone_re = re.compile(r'(?:\+?\d{1,3}[\s-]?)?(?:\(?\d{3}\)?[\s-]?)?\d{3}[\s-]?\d{4}', re.I)

def extract_text_pdf(path):
    text = []
    with pdfplumber.open(path) as pdf:
        for p in pdf.pages:
            t = p.extract_text() or ''
            text.append(t)
    return '\n'.join(text)

def ocr_pdf(path):
    # render pages and OCR via pytesseract
    text = []
    import fitz  # PyMuPDF
    doc = fitz.open(path)
    for page in doc:
        pix = page.get_pixmap()
        img = Image.frombytes('RGB', [pix.width, pix.height], pix.samples)
        t = pytesseract.image_to_string(img)
        text.append(t)
    return '\n'.join(text)

@app.post('/parse')
async def parse(file: UploadFile = File(...)):
    ext = os.path.splitext(file.filename)[1].lower()
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
    content = await file.read()
    tmp.write(content); tmp.flush(); tmp.close()
    text = ''
    try:
        if ext == '.pdf':
            text = extract_text_pdf(tmp.name)
            if not text.strip():
                text = ocr_pdf(tmp.name)
        else:
            text = docx2txt.process(tmp.name)
    except Exception as e:
        return {'error': 'extraction_failed', 'details': str(e)}
    # basic NER + heuristics
    doc = nlp(text)
    names = [ent.text for ent in doc.ents if ent.label_ == 'PERSON']
    emails = re.findall(email_re, text)
    phones = re.findall(phone_re, text)
    skills = []
    # naive skill extraction using token match (extendable)
    skill_candidates = ['python','machine learning','nlp','aws','docker','kubernetes','sql','pandas','numpy','tensorflow','pytorch']
    lower = text.lower()
    for s in skill_candidates:
        if s in lower and s not in skills:
            skills.append(s)
    # years of experience heuristic

    exp = re.search(r'(\d+)\+?\s+years', lower)
    exp_years = int(exp.group(1)) if exp else None
    parsed = {
        'name': names[0] if names else None,
        'emails': emails,
        'phones': phones,
        'skills': skills,
        'experience_years': exp_years,
        'raw_text': text
    }
    return parsed
