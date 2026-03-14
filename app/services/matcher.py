from functools import lru_cache

from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.config import settings
from app.utils.text import clean_text, extract_skills


@lru_cache(maxsize=1)
def get_model() -> SentenceTransformer:
    return SentenceTransformer(settings.MODEL_NAME)


class ResumeMatcherService:
    JD_KEYWORDS = [
        "responsibilities",
        "requirements",
        "qualifications",
        "job description",
        "skills",
        "preferred",
        "desired",
        "job summary",
        "position",
        "job title",
    ]
    RESUME_KEYWORDS = [
        "education",
        "projects",
        "certifications",
        "linkedin",
        "experience",
        "internship",
        "objective",
    ]

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

    def jd_confidence(self, text: str, filename: str) -> int:
        normalized = clean_text(text).lower()
        jd_score = sum(normalized.count(k) for k in self.JD_KEYWORDS)
        resume_score = sum(normalized.count(k) for k in self.RESUME_KEYWORDS)
        filename_hint = "jd" in filename.lower() or "description" in filename.lower()
        return jd_score + (20 if filename_hint else 0) - resume_score

    def is_probable_jd(self, text: str, filename: str) -> bool:
        return self.jd_confidence(text, filename) > 0

    def extract_top_keywords(self, jd_text: str, resume_text: str, top_n: int = 5) -> list[str]:
        try:
            vectorizer = TfidfVectorizer(stop_words="english")
            tfidf = vectorizer.fit_transform([jd_text, resume_text])
            feature_names = vectorizer.get_feature_names_out()
            diff = tfidf[0] - tfidf[1]
            abs_diff = abs(diff.toarray()[0])
            top_indices = abs_diff.argsort()[-top_n:][::-1]
            return [feature_names[i] for i in top_indices]
        except Exception:
            return []
