import io
import re
import pdfplumber
from loguru import logger


def _ocr_pdf_bytes(file_bytes: bytes) -> str:
    """OCR fallback for scanned/image PDFs using PyMuPDF + pytesseract."""
    try:
        import fitz  # PyMuPDF
        import pytesseract
        from PIL import Image
        import numpy as np

        doc = fitz.open(stream=file_bytes, filetype="pdf")
        pages = []
        for page_num in range(min(len(doc), 8)):  # cap at 8 pages
            page = doc[page_num]
            mat = fitz.Matrix(2.0, 2.0)  # 2x zoom = 144 DPI for better OCR
            pix = page.get_pixmap(matrix=mat, colorspace=fitz.csRGB)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            text = pytesseract.image_to_string(img, config="--psm 6")
            if text.strip():
                pages.append(text)
        doc.close()
        result = "\n\n".join(pages)
        logger.info(f"OCR extracted {len(result)} chars from scanned PDF")
        return result
    except Exception as e:
        logger.error(f"OCR fallback failed: {e}")
        return ""


def extract_text_from_pdf(file_bytes: bytes) -> str:
    # Layer 1: pdfplumber (fast, handles text-based PDFs)
    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            pages = []
            for page in pdf.pages:
                text = page.extract_text(x_tolerance=3, y_tolerance=3)
                if text:
                    pages.append(text)
            text = "\n\n".join(pages)
            if len(text.strip()) > 100:
                return text
    except Exception as e:
        logger.warning(f"pdfplumber failed: {e}")

    # Layer 2: OCR for scanned/image PDFs
    logger.info("Text layer empty — attempting OCR on scanned PDF")
    return _ocr_pdf_bytes(file_bytes)


def clean_resume_text(text: str) -> str:
    # Remove excessive whitespace
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r" {2,}", " ", text)
    # Remove common non-text artifacts
    text = re.sub(r"[^\x00-\x7F]+", " ", text)
    return text.strip()


def extract_sections(text: str) -> dict[str, str]:
    """Best-effort section extraction from resume text."""
    section_headers = {
        "skills": r"(?i)(technical\s+skills?|skills?|technologies|core\s+competencies)",
        "experience": r"(?i)(work\s+experience|professional\s+experience|experience|employment)",
        "education": r"(?i)(education|academic|qualifications)",
        "projects": r"(?i)(projects?|portfolio|personal\s+projects?)",
        "summary": r"(?i)(summary|objective|profile|about)",
    }
    lines = text.split("\n")
    sections: dict[str, list[str]] = {"raw": lines, "full": [text]}
    current_section = "other"
    section_content: dict[str, list[str]] = {k: [] for k in section_headers}

    for line in lines:
        matched = False
        for section_name, pattern in section_headers.items():
            if re.match(pattern, line.strip()) and len(line.strip()) < 60:
                current_section = section_name
                matched = True
                break
        if not matched and current_section in section_content:
            section_content[current_section].append(line)

    return {k: "\n".join(v).strip() for k, v in section_content.items()}


def extract_contact_info(text: str) -> dict:
    email_match = re.search(r"[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}", text)
    phone_match = re.search(r"(\+?1?\s?)?(\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4})", text)
    linkedin_match = re.search(r"linkedin\.com/in/[\w-]+", text)
    github_match = re.search(r"github\.com/[\w-]+", text)
    name_lines = [l.strip() for l in text.split("\n")[:5] if l.strip() and len(l.strip().split()) >= 2]

    return {
        "name": name_lines[0] if name_lines else "",
        "email": email_match.group(0) if email_match else "",
        "phone": phone_match.group(0) if phone_match else "",
        "linkedin": linkedin_match.group(0) if linkedin_match else "",
        "github": github_match.group(0) if github_match else "",
    }
