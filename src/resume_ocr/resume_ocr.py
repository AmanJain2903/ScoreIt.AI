# Example usage:
# sample_pdf_path = "data/pdf_resumes/cv (1).pdf"
# with open(sample_pdf_path, "rb") as f:
#     sample_pdf_bytes = f.read()

# ocr = ResumeOCR()

# print("Trying with pdfPath")
# ocr.setInputs(pdfPath=sample_pdf_path)
# print(ocr.extractText())
# ocr.resetOCR()

# print("Trying with pdfBytes")
# ocr.setInputs(pdfBytes=sample_pdf_bytes)
# print(ocr.extractText())
# ocr.resetOCR()

import fitz

class ResumeOCR:
    def __init__(self):
        self.pdfPath = None
        self.pdfBytes = None
        self.resumeText = ""
    
    def setInputs(self, pdfPath=None, pdfBytes=None):
        if pdfPath is None and pdfBytes is None:
            raise ValueError("Either pdfPath or pdfBytes must be provided.")
        if pdfPath is not None and pdfBytes is not None:
            raise ValueError("Only one of pdfPath or pdfBytes should be provided.")
        if pdfPath:
            if not isinstance(pdfPath, str):
                raise TypeError("pdfPath must be a string.")
            self.pdfPath = pdfPath
        if pdfBytes:
            if not isinstance(pdfBytes, bytes):
                raise TypeError("pdfBytes must be bytes.")
            self.pdfBytes = pdfBytes
    
    def extractText(self):
        if self.resumeText:
            return self.resumeText
        if not self.pdfPath and not self.pdfBytes:
            raise ValueError("pdfPath or pdfBytes must be set before extracting text.")
        text = ""
        if self.pdfPath:
            with fitz.open(self.pdfPath) as doc:
                for page in doc:
                    text += page.get_text()
        else:
            with fitz.open(stream=self.pdfBytes, filetype="pdf") as doc:
                for page in doc:
                    text += page.get_text()
        
        self.resumeText = text
        return self.resumeText

    def resetOCR(self):
        self.pdfPath = None
        self.pdfBytes = None
        self.resumeText = ""




