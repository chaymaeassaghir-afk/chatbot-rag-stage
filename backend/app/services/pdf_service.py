from pathlib import Path
import shutil
import fitz   # PyMuPDF

BASE_DIR = Path(__file__).resolve().parents[3]

UPLOAD_FOLDER = BASE_DIR / "data" / "uploads"

UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

class PDFService:

    @staticmethod
    def save(file):

        destination = UPLOAD_FOLDER / file.filename

        with open(destination, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return destination
    @staticmethod
    def extract_text(pdf_path):

        document = fitz.open(pdf_path)

        text = ""

        for page in document:

            text += page.get_text()

        document.close()

        return text    