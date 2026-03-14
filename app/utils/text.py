import re
from typing import List


DEFAULT_SKILL_KEYWORDS = {
    "python",
    "java",
    "javascript",
    "typescript",
    "php",
    "sql",
    "mysql",
    "postgresql",
    "mongodb",
    "docker",
    "kubernetes",
    "git",
    "linux",
    "fastapi",
    "flask",
    "django",
    "laravel",
    "spring",
    "react",
    "vue",
    "nodejs",
    "node.js",
    "html",
    "css",
    "rest",
    "api",
    "aws",
    "azure",
    "gcp",
    "machine learning",
    "deep learning",
    "nlp",
    "pytorch",
    "tensorflow",
    "pandas",
    "numpy",
    "scikit-learn",
    "power bi",
    "excel",
    "communication",
    "leadership",
    "problem solving",
    "english",
}


def clean_text(text: str) -> str:
    if not text:
        return ""
    text = text.replace("\x00", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def normalize_text(text: str) -> str:
    return clean_text(text).lower()


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
