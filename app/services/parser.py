from io import BytesIO
from typing import Optional

import pdfplumber
from docx import Document
from fastapi import UploadFile

from app.utils.text import clean_text


class ResumeParserError(Exception):
    pass


class ResumeParserService:
    SUPPORTED_TYPES = {
        ".pdf",
        ".docx",
        ".txt",
    }

    @staticmethod
    def get_extension(filename: Optional[str]) -> str:
        if not filename or "." not in filename:
            return ""
        return "." + filename.lower().split(".")[-1]

    async def parse_upload_file(self, file: UploadFile) -> str:
        ext = self.get_extension(file.filename)
        content = await file.read()

        if not content:
            raise ResumeParserError(f"File '{file.filename}' is empty.")

        if ext == ".pdf":
            return self._parse_pdf(content)
        if ext == ".docx":
            return self._parse_docx(content)
        if ext == ".txt":
            return self._parse_txt(content)

        raise ResumeParserError(
            f"Unsupported file format for '{file.filename}'. Only PDF, DOCX, TXT are allowed."
        )

    def _parse_pdf(self, content: bytes) -> str:
        try:
            pages_text = []
            with pdfplumber.open(BytesIO(content)) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text() or ""
                    pages_text.append(page_text)
            return clean_text("\n".join(pages_text))
        except Exception as exc:
            raise ResumeParserError(f"Failed to parse PDF: {exc}") from exc

    def _parse_docx(self, content: bytes) -> str:
        try:
            doc = Document(BytesIO(content))
            lines = [para.text for para in doc.paragraphs if para.text]
            return clean_text("\n".join(lines))
        except Exception as exc:
            raise ResumeParserError(f"Failed to parse DOCX: {exc}") from exc

    def _parse_txt(self, content: bytes) -> str:
        try:
            return clean_text(content.decode("utf-8", errors="ignore"))
        except Exception as exc:
            raise ResumeParserError(f"Failed to parse TXT: {exc}") from exc
