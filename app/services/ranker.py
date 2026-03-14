import re
from typing import Dict, List

from fastapi import UploadFile

from app.schemas import RankedCandidate, RankResponse
from app.services.matcher import ResumeMatcherService
from app.services.parser import ResumeParserError, ResumeParserService
from app.utils.text import clean_text, preview_text


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

    async def _parse_files(self, files: List[UploadFile]) -> tuple[Dict[str, str], list[str]]:
        text_data: Dict[str, str] = {}
        parse_errors: list[str] = []

        for file in files:
            filename = file.filename or "unknown"
            try:
                text = await self.parser.parse_upload_file(file)
                text_data[filename] = text
            except ResumeParserError as exc:
                parse_errors.append(f"{filename}: {exc}")

        return text_data, parse_errors

    def _classify_documents(
        self, text_data: Dict[str, str]
    ) -> tuple[Dict[str, str], Dict[str, str]]:
        jd_files: Dict[str, str] = {}
        resume_files: Dict[str, str] = {}

        for filename, text in text_data.items():
            if self.matcher.is_probable_jd(text, filename):
                jd_files[filename] = text
            else:
                resume_files[filename] = text

        if not jd_files and len(text_data) >= 2:
            best_jd = max(
                text_data.items(),
                key=lambda item: self.matcher.jd_confidence(item[1], item[0]),
            )
            jd_files[best_jd[0]] = best_jd[1]
            resume_files = {k: v for k, v in text_data.items() if k != best_jd[0]}

        return jd_files, resume_files

    async def rank_resumes(
        self, jd_text: str, files: List[UploadFile], top_k: int | None = None
    ) -> RankResponse:
        jd_text = clean_text(jd_text)
        if not jd_text:
            raise ValueError("Job description must not be empty.")

        text_data, parse_errors = await self._parse_files(files)
        results: list[RankedCandidate] = []

        for filename, resume_text in text_data.items():
            score = self.matcher.similarity_score(jd_text, resume_text)
            matched_skills, missing_skills, extracted_skills = self.matcher.compare_skills(
                jd_text, resume_text
            )
            top_keywords = self.matcher.extract_top_keywords(jd_text, resume_text)

            results.append(
                RankedCandidate(
                    filename=filename,
                    candidate_name=self.extract_candidate_name(resume_text, filename),
                    score=score,
                    matched_skills=matched_skills,
                    missing_skills=missing_skills,
                    extracted_skills=extracted_skills,
                    top_keywords=top_keywords,
                    extracted_text_preview=preview_text(resume_text),
                )
            )

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

    async def rank_documents_auto(
        self, files: List[UploadFile], top_k: int | None = None
    ) -> RankResponse:
        if len(files) < 2:
            raise ValueError("Please upload at least 1 JD and 1 resume file.")

        text_data, parse_errors = await self._parse_files(files)
        if len(text_data) < 2:
            raise ValueError("Could not parse enough files to classify JD and resumes.")

        jd_files, resume_files = self._classify_documents(text_data)
        if not jd_files:
            raise ValueError("No Job Description detected.")
        if not resume_files:
            raise ValueError("No resumes detected.")

        results: list[RankedCandidate] = []
        for resume_name, resume_text in resume_files.items():
            best_candidate: RankedCandidate | None = None
            
            for jd_name, jd_text in jd_files.items():
                score = self.matcher.similarity_score(jd_text, resume_text)
                matched_skills, missing_skills, extracted_skills = self.matcher.compare_skills(
                    jd_text, resume_text
                )
                top_keywords = self.matcher.extract_top_keywords(jd_text, resume_text)

                candidate = RankedCandidate(
                    filename=resume_name,
                    candidate_name=self.extract_candidate_name(resume_text, resume_name),
                    compared_jd=jd_name,
                    score=score,
                    matched_skills=matched_skills,
                    missing_skills=missing_skills,
                    extracted_skills=extracted_skills,
                    top_keywords=top_keywords,
                    extracted_text_preview=preview_text(resume_text),
                )
                
                # Chỉ giữ lại kết quả tốt nhất của CV này với JD phù hợp nhất
                if best_candidate is None or score > best_candidate.score:
                    best_candidate = candidate
            
            if best_candidate:
                results.append(best_candidate)

        if not results and parse_errors:
            raise ValueError("All uploaded files failed to parse: " + " | ".join(parse_errors))

        results.sort(key=lambda item: item.score, reverse=True)
        if top_k is not None and top_k > 0:
            results = results[:top_k]

        first_jd_text = next(iter(jd_files.values()))
        jd_preview = preview_text(first_jd_text)
        if len(jd_files) > 1:
            jd_preview = f"Detected {len(jd_files)} JD files. Example: {jd_preview}"

        return RankResponse(
            jd_preview=jd_preview,
            total_files=len(results),
            ranked_candidates=results,
        )
