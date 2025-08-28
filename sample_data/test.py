from docx import Document

doc_path = "C:/Users/somil shekhar/Downloads/John Doe.docx"
doc = Document(doc_path)
full_text = "\n".join([p.text for p in doc.paragraphs])
print(full_text)
