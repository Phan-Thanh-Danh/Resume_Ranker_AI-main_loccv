# Resume_Ranker_AI → FastAPI ATS API refactor

Dưới đây là bản refactor đầy đủ để bỏ Gradio UI, chuyển sang FastAPI, dùng Sentence Transformers để match JD ↔ CV, phù hợp tích hợp trực tiếp vào HRM/ATS.

---

## Cấu trúc repo mới

```text
Resume_Ranker_AI/
├─ app/
│  ├─ __init__.py
│  ├─ main.py
│  ├─ config.py
│  ├─ schemas.py
│  ├─ services/
│  │  ├─ __init__.py
│  │  ├─ parser.py
│  │  ├─ matcher.py
│  │  └─ ranker.py
│  └─ utils/
│     ├─ __init__.py
│     └─ text.py
├─ requirements.txt
├─ .env.example
├─ README.md
└─ run.py
```

---

## 1) `requirements.txt`

```txt
fastapi==0.115.8
uvicorn[standard]==0.34.0
python-multipart==0.0.20
sentence-transformers==3.4.1
torch>=2.2.0
pdfplumber==0.11.5
python-docx==1.1.2
pydantic==2.10.6
pydantic-settings==2.7.1
scikit-learn==1.6.1
numpy==1.26.4
```

---

## 2) `.env.example`

```env
APP_NAME=Resume Ranking API
APP_ENV=development
APP_HOST=0.0.0.0
APP_PORT=8000
MODEL_NAME=sentence-transformers/all-MiniLM-L6-v2
MAX_FILE_SIZE_MB=10
TOP_K_DEFAULT=10
```

---

## 3) `app/config.py`

```python
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Resume Ranking API"
    APP_ENV: str = "development"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"
    MAX_FILE_SIZE_MB: int = 10
    TOP_K_DEFAULT: int = 10

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()
```

---

## 4) `app/schemas.py`

```python
from typing import List, Optional
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    app: str
    model: str


class RankedCandidate(BaseModel):
    filename: str
    candidate_name: Optional[str] = None
    score: float = Field(..., ge=0, le=100)
    matched_skills: List[str] = []
    missing_skills: List[str] = []
    extracted_skills: List[str] = []
    extracted_text_preview: str


class RankResponse(BaseModel):
    jd_preview: str
    total_files: int
    ranked_candidates: List[RankedCandidate]


class ErrorResponse(BaseModel):
    detail: str
```

---

## 5) `app/utils/text.py`

```python
import re
from typing import List


DEFAULT_SKILL_KEYWORDS = {
    "python", "java", "javascript", "typescript", "php", "sql", "mysql",
    "postgresql", "mongodb", "docker", "kubernetes", "git", "linux",
    "fastapi", "flask", "django", "laravel", "spring", "react", "vue",
    "nodejs", "node.js", "html", "css", "rest", "api", "aws", "azure",
    "gcp", "machine learning", "deep learning", "nlp", "pytorch", "tensorflow",
    "pandas", "numpy", "scikit-learn", "power bi", "excel", "communication",
    "leadership", "problem solving", "english"
}


def clean_text(text: str) -> str:
    if not text:
        return ""
    text = text.replace("\x00", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def normalize_text(text: str) -> str:
    text = clean_text(text).lower()
    return text


def extract_skills(text: str, skill_set: set[str] | None = None) -> List[str]:
    source = normalize_text(text)
    skills = skill_set or DEFAULT_SKILL_KEYWORDS
    found = []

    for skill in skills:
        pattern = r"(?<!\w)" + re.escape(skill.lower()) + r"(?!\w)"
        if re.search(pattern, source):
            found.append(skill)

    return sorted(set(found))


def preview_text(text: str, max_len: int = 250) -> str:
    text = clean_text(text)
    if len(text) <= max_len:
        return text
    return text[:max_len].rstrip() + "..."
```

---

## 6) `app/services/parser.py`

```python
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
```

---

## 7) `app/services/matcher.py`

```python
from functools import lru_cache
from typing import Iterable

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from app.config import settings
from app.utils.text import extract_skills


@lru_cache(maxsize=1)
def get_model() -> SentenceTransformer:
    return SentenceTransformer(settings.MODEL_NAME)


class ResumeMatcherService:
    def __init__(self) -> None:
        self.model = get_model()

    def similarity_score(self, jd_text: str, resume_text: str) -> float:
        embeddings = self.model.encode([jd_text, resume_text], normalize_embeddings=True)
        score = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
        return round(float(score) * 100, 2)

    def compare_skills(self, jd_text: str, resume_text: str) -> tuple[list[str], list[str], list[str]]:
        jd_skills = set(extract_skills(jd_text))
        resume_skills = set(extract_skills(resume_text))

        matched = sorted(jd_skills.intersection(resume_skills))
        missing = sorted(jd_skills.difference(resume_skills))
        extracted = sorted(resume_skills)

        return matched, missing, extracted
```

---

## 8) `app/services/ranker.py`

```python
import re
from typing import List

from fastapi import UploadFile

from app.schemas import RankedCandidate, RankResponse
from app.services.matcher import ResumeMatcherService
from app.services.parser import ResumeParserError, ResumeParserService
from app.utils.text import preview_text, clean_text


class ResumeRankerService:
    def __init__(self) -> None:
        self.parser = ResumeParserService()
        self.matcher = ResumeMatcherService()

    @staticmethod
    def extract_candidate_name(text: str, fallback_filename: str) -> str:
        lines = [line.strip() for line in re.split(r"[\r\n]+", text) if line.strip()]
        if lines:
            first_line = lines[0]
            if 2 <= len(first_line.split()) <= 6 and len(first_line) <= 60:
                return first_line
        return fallback_filename.rsplit(".", 1)[0]

    async def rank_resumes(self, jd_text: str, files: List[UploadFile], top_k: int | None = None) -> RankResponse:
        jd_text = clean_text(jd_text)
        if not jd_text:
            raise ValueError("Job description must not be empty.")

        results: list[RankedCandidate] = []
        parse_errors: list[str] = []

        for file in files:
            try:
                resume_text = await self.parser.parse_upload_file(file)
                score = self.matcher.similarity_score(jd_text, resume_text)
                matched_skills, missing_skills, extracted_skills = self.matcher.compare_skills(jd_text, resume_text)

                results.append(
                    RankedCandidate(
                        filename=file.filename or "unknown",
                        candidate_name=self.extract_candidate_name(resume_text, file.filename or "unknown"),
                        score=score,
                        matched_skills=matched_skills,
                        missing_skills=missing_skills,
                        extracted_skills=extracted_skills,
                        extracted_text_preview=preview_text(resume_text),
                    )
                )
            except ResumeParserError as exc:
                parse_errors.append(f"{file.filename}: {exc}")

        if not results and parse_errors:
            raise ValueError("All uploaded resumes failed to parse: " + " | ".join(parse_errors))

        results.sort(key=lambda item: item.score, reverse=True)
        if top_k is not None and top_k > 0:
            results = results[:top_k]

        return RankResponse(
            jd_preview=preview_text(jd_text),
            total_files=len(results),
            ranked_candidates=results,
        )
```

---

## 9) `app/main.py`

```python
from typing import List, Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.schemas import ErrorResponse, HealthResponse, RankResponse
from app.services.ranker import ResumeRankerService

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="FastAPI ATS Resume Screening API using Sentence Transformers",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ranker_service = ResumeRankerService()


@app.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    return HealthResponse(
        status="ok",
        app=settings.APP_NAME,
        model=settings.MODEL_NAME,
    )


@app.post(
    "/api/v1/rank-resumes",
    response_model=RankResponse,
    responses={400: {"model": ErrorResponse}},
)
async def rank_resumes(
    jd_text: str = Form(..., description="Job description text"),
    top_k: Optional[int] = Form(None, description="Limit number of ranked results"),
    files: List[UploadFile] = File(..., description="Resume files: PDF, DOCX, TXT"),
) -> RankResponse:
    if not files:
        raise HTTPException(status_code=400, detail="At least one resume file is required.")

    for file in files:
        if file.size and file.size > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail=f"File '{file.filename}' exceeds {settings.MAX_FILE_SIZE_MB} MB limit.",
            )

    try:
        return await ranker_service.rank_resumes(jd_text=jd_text, files=files, top_k=top_k)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
```

---

## 10) `app/__init__.py`

```python
```

---

## 11) `app/services/__init__.py`

```python
```

---

## 12) `app/utils/__init__.py`

```python
```

---

## 13) `run.py`

```python
import uvicorn

from app.config import settings


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.APP_ENV == "development",
    )
```

---

## 14) `README.md`

````md
# Resume Ranking API

Refactor from Gradio UI to FastAPI for HRM/ATS integration.

## Features
- Upload multiple CV files: PDF, DOCX, TXT
- Match CV against JD using Sentence Transformers
- Return similarity score
- Extract matched skills / missing skills
- Ready to plug into HRM backend

## Setup

### Python version
Recommended: Python 3.10 or 3.11

### Install
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
````

### Run

```bash
python run.py
```

API docs:

* Swagger UI: `http://127.0.0.1:8000/docs`
* Health: `http://127.0.0.1:8000/health`

## Endpoint

### `POST /api/v1/rank-resumes`

Form-data:

* `jd_text`: string
* `top_k`: integer (optional)
* `files`: multiple resume files

### Example response

```json
{
  "jd_preview": "Backend Python developer with FastAPI, Docker, SQL...",
  "total_files": 2,
  "ranked_candidates": [
    {
      "filename": "candidate_a.pdf",
      "candidate_name": "Nguyen Van A",
      "score": 84.73,
      "matched_skills": ["python", "fastapi", "docker", "sql"],
      "missing_skills": ["kubernetes"],
      "extracted_skills": ["docker", "fastapi", "python", "sql"],
      "extracted_text_preview": "Nguyen Van A ..."
    }
  ]
}
```

## HRM integration flow

1. HR tạo JD trong hệ thống.
2. Applicant upload CV.
3. HRM gọi endpoint `/api/v1/rank-resumes`.
4. API trả về score + matched/missing skills.
5. Hệ thống lưu ranking vào DB và hiển thị dashboard tuyển dụng.

````

---

## Cách gọi API từ HRM PHP

```php
<?php
$ch = curl_init();

$data = [
    'jd_text' => 'Backend Python developer with FastAPI, Docker, SQL',
    'top_k' => 10,
    'files[0]' => new CURLFile('C:/cv/candidate_a.pdf'),
    'files[1]' => new CURLFile('C:/cv/candidate_b.docx'),
];

curl_setopt_array($ch, [
    CURLOPT_URL => 'http://127.0.0.1:8000/api/v1/rank-resumes',
    CURLOPT_POST => true,
    CURLOPT_POSTFIELDS => $data,
    CURLOPT_RETURNTRANSFER => true,
]);

$response = curl_exec($ch);
curl_close($ch);

echo $response;
````

---

## Ghi chú triển khai thật cho HRM

* Nên tách parser và ranker thành service riêng nếu scale lớn.
* Nên lưu text CV đã parse vào DB để tránh parse lại.
* Nên cache embedding JD nếu một JD được dùng nhiều lần.
* Nên thêm bảng `recruitment_candidates`, `candidate_resume_scores`, `job_descriptions` trong HRM.
* Nên log kết quả screening để HR audit lại.

---

## Bảng DB gợi ý cho HRM

```sql
CREATE TABLE job_descriptions (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(255) NOT NULL,
    description LONGTEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE recruitment_candidates (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    full_name VARCHAR(255) NULL,
    email VARCHAR(255) NULL,
    phone VARCHAR(50) NULL,
    resume_file_path VARCHAR(500) NULL,
    resume_text LONGTEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE candidate_resume_scores (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    job_description_id BIGINT NOT NULL,
    candidate_id BIGINT NOT NULL,
    score DECIMAL(5,2) NOT NULL,
    matched_skills JSON NULL,
    missing_skills JSON NULL,
    extracted_skills JSON NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (job_description_id) REFERENCES job_descriptions(id),
    FOREIGN KEY (candidate_id) REFERENCES recruitment_candidates(id)
);
```

---

## Lệnh chạy trên Windows PowerShell

```powershell
py -3.11 -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python run.py
```
