from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.config import settings
from app.schemas import ErrorResponse, HealthResponse, RankResponse
from app.services.ranker import ResumeRankerService

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="API Chấm điểm và Xếp hạng CV tự động sử dụng Sentence Transformers",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ranker_service = ResumeRankerService()
BASE_DIR = Path(__file__).resolve().parent
UI_FILE = BASE_DIR / "static" / "index.html"


@app.get("/", include_in_schema=False)
def ui() -> FileResponse:
    return FileResponse(UI_FILE)


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
    jd_text: str = Form(..., description="Văn bản mô tả công việc (JD)"),
    top_k: Optional[int] = Form(None, description="Giới hạn số lượng kết quả trả về"),
    files: List[UploadFile] = File(..., description="Danh sách file CV: PDF, DOCX, TXT"),
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


@app.post(
    "/api/v1/rank-documents-auto",
    response_model=RankResponse,
    responses={400: {"model": ErrorResponse}},
)
async def rank_documents_auto(
    top_k: Optional[int] = Form(None, description="Giới hạn số lượng kết quả trả về"),
    files: List[UploadFile] = File(..., description="File JD và CV kết hợp: PDF, DOCX, TXT"),
) -> RankResponse:
    if not files:
        raise HTTPException(status_code=400, detail="At least one file is required.")

    for file in files:
        if file.size and file.size > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail=f"File '{file.filename}' exceeds {settings.MAX_FILE_SIZE_MB} MB limit.",
            )

    try:
        return await ranker_service.rank_documents_auto(files=files, top_k=top_k)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post(
    "/api/v1/rank",
    response_model=RankResponse,
    responses={400: {"model": ErrorResponse}},
)
async def rank_documents(
    jd_text: Optional[str] = Form(None, description="Văn bản mô tả công việc (Tùy chọn)"),
    top_k: Optional[int] = Form(None, description="Giới hạn số lượng kết quả trả về"),
    files: List[UploadFile] = File(..., description="File CV, hoặc file JD/CV kết hợp"),
) -> RankResponse:
    if not files:
        raise HTTPException(status_code=400, detail="At least one file is required.")

    for file in files:
        if file.size and file.size > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail=f"File '{file.filename}' exceeds {settings.MAX_FILE_SIZE_MB} MB limit.",
            )

    try:
        if jd_text and jd_text.strip():
            return await ranker_service.rank_resumes(jd_text=jd_text, files=files, top_k=top_k)
        return await ranker_service.rank_documents_auto(files=files, top_k=top_k)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post(
    "/api/v1/rank-with-jd-file",
    response_model=RankResponse,
    responses={400: {"model": ErrorResponse}},
)
async def rank_with_jd_file(
    top_k: Optional[int] = Form(None, description="Giới hạn số lượng kết quả trả về"),
    jd_files: List[UploadFile] = File(..., description="File JD: PDF, DOCX, TXT"),
    cv_files: List[UploadFile] = File(..., description="Danh sách file CV: PDF, DOCX, TXT"),
) -> RankResponse:
    """Xếp hạng CV dựa trên file JD được tải lên rõ ràng."""
    if not jd_files:
        raise HTTPException(status_code=400, detail="Vui lòng tải lên ít nhất 1 file JD.")
    if not cv_files:
        raise HTTPException(status_code=400, detail="Vui lòng tải lên ít nhất 1 file CV.")

    all_files = list(jd_files) + list(cv_files)
    for file in all_files:
        if file.size and file.size > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail=f"File '{file.filename}' vượt quá giới hạn {settings.MAX_FILE_SIZE_MB} MB.",
            )

    try:
        # Parse all JD files and concatenate their content
        jd_texts = []
        for jd_file in jd_files:
            jd_text_parsed = await ranker_service.parser.parse_upload_file(jd_file)
            jd_texts.append(jd_text_parsed)
        combined_jd = "\n\n".join(jd_texts)

        if not combined_jd.strip():
            raise HTTPException(status_code=400, detail="Không thể đọc nội dung từ file JD.")

        return await ranker_service.rank_resumes(
            jd_text=combined_jd, files=cv_files, top_k=top_k
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
