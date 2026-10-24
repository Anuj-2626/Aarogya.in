from pathlib import Path
import shutil

import pymupdf
import pytesseract
from PIL import Image


TESSERACT_LANGUAGE_MAP = {
    "en": "eng",
    "hi": "hin",
    "mr": "mar",
    "bn": "ben",
    "ta": "tam",
}


# Project-local Tesseract language data directory.
# Backend/
# ├── app/
# └── tessdata/
TESSDATA_DIR = Path(__file__).resolve().parents[2] / "tessdata"


class OCRService:

    def __init__(self):
        tesseract_path = shutil.which("tesseract")

        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path

        if not TESSDATA_DIR.exists():
            raise FileNotFoundError(
                f"Tesseract tessdata directory not found: {TESSDATA_DIR}"
            )

    def _get_tesseract_language(
        self,
        language_code: str
    ) -> str:

        return TESSERACT_LANGUAGE_MAP.get(
            language_code,
            "eng"
        )

    def _get_tesseract_config(self) -> str:
        return f'--tessdata-dir "{TESSDATA_DIR}"'

    def extract_text(
        self,
        file_path: str,
        file_type: str,
        language_code: str = "en"
    ) -> str:

        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                "Medical document file not found"
            )

        if file_type in {"jpg", "png"}:
            return self._extract_from_image(
                path,
                language_code
            )

        if file_type == "pdf":
            return self._extract_from_pdf(
                path,
                language_code
            )

        if file_type == "docx":
            return self._extract_from_docx(path)

        raise ValueError(
            f"Unsupported OCR file type: {file_type}"
        )

    def _extract_from_image(
        self,
        path: Path,
        language_code: str
    ) -> str:

        image = Image.open(path)

        text = pytesseract.image_to_string(
            image,
            lang=self._get_tesseract_language(
                language_code
            ),
            config=self._get_tesseract_config()
        )

        return text.strip()

    def _extract_from_pdf(
        self,
        path: Path,
        language_code: str
    ) -> str:

        document = pymupdf.open(path)

        extracted_pages = []

        for page in document:

            text = page.get_text().strip()

            if text:
                extracted_pages.append(text)
                continue

            pixmap = page.get_pixmap(
                matrix=pymupdf.Matrix(2, 2)
            )

            image = Image.frombytes(
                "RGB",
                [pixmap.width, pixmap.height],
                pixmap.samples
            )

            ocr_text = pytesseract.image_to_string(
                image,
                lang=self._get_tesseract_language(
                    language_code
                ),
                config=self._get_tesseract_config()
            ).strip()

            if ocr_text:
                extracted_pages.append(
                    ocr_text
                )

        document.close()

        return "\n\n".join(extracted_pages)

    def _extract_from_docx(
        self,
        path: Path
    ) -> str:

        from docx import Document

        document = Document(path)

        paragraphs = [
            paragraph.text.strip()
            for paragraph in document.paragraphs
            if paragraph.text.strip()
        ]

        return "\n".join(paragraphs)


ocr_service = OCRService()