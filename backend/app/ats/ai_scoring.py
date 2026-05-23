import re
from typing import List


SKILL_KEYWORDS = [
    "python", "java", "javascript", "typescript", "react", "angular", "vue",
    "node", "express", "django", "flask", "fastapi", "spring", "sql", "nosql",
    "mongodb", "postgresql", "mysql", "redis", "docker", "kubernetes", "aws",
    "azure", "gcp", "git", "ci/cd", "rest", "graphql", "html", "css", "sass",
    "tailwind", "bootstrap", "machine learning", "deep learning", "nlp",
    "tensorflow", "pytorch", "scikit-learn", "pandas", "numpy", "spark",
    "hadoop", "kafka", "rabbitmq", "microservices", "api", "agile", "scrum",
    "linux", "bash", "powershell", "terraform", "ansible", "jenkins",
    "prometheus", "grafana", "elasticsearch", "snowflake", "bigquery",
]


def extract_text_from_pdf(file_bytes: bytes) -> str:
    try:
        from PyPDF2 import PdfReader
        import io
        reader = PdfReader(io.BytesIO(file_bytes))
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        if text.strip():
            return text
    except Exception:
        pass
    try:
        return file_bytes.decode("utf-8", errors="ignore")
    except Exception:
        pass
    try:
        import zipfile
        import xml.etree.ElementTree as ET
        import io
        zf = zipfile.ZipFile(io.BytesIO(file_bytes))
        xml_content = zf.read("word/document.xml")
        root = ET.fromstring(xml_content)
        ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
        texts = []
        for t in root.iter("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t"):
            if t.text:
                texts.append(t.text)
        if texts:
            return " ".join(texts)
    except Exception:
        pass
    return ""


def extract_skills(cv_text: str) -> List[str]:
    text_lower = cv_text.lower()
    found = []
    for skill in SKILL_KEYWORDS:
        pattern = re.compile(r'\b' + re.escape(skill) + r'\b', re.IGNORECASE)
        if pattern.search(text_lower):
            found.append(skill)
    return list(set(found))


def extract_experience_years(cv_text: str) -> float:
    patterns = [
        r'(\d+)\+?\s*years?\s*(?:of\s+)?experience',
        r'experience\s*(?:of\s+)?(\d+)\+?\s*years?',
        r'(\d+)\+?\s*yr?s?\s*(?:of\s+)?exp',
    ]
    for pattern in patterns:
        match = re.search(pattern, cv_text.lower())
        if match:
            return float(match.group(1))

    years_in_dates = re.findall(r'(19|20)\d{2}', cv_text)
    if years_in_dates:
        years = sorted([int(y) for y in years_in_dates])
        span = years[-1] - years[0]
        return max(0.0, min(span, 30.0))
    return 0.0


def compute_keywords_match(cv_text: str, job_keywords: List[str]) -> float:
    if not job_keywords:
        return 0.0
    text_lower = cv_text.lower()
    matched = sum(1 for kw in job_keywords if kw.lower() in text_lower)
    return matched / len(job_keywords)


def score_cv(cv_text: str, job_keywords: List[str] = None) -> dict:
    job_keywords = job_keywords or []
    skills = extract_skills(cv_text)
    exp_years = extract_experience_years(cv_text)
    tech_skills_match = len(skills) / max(len(SKILL_KEYWORDS), 1) * 100
    keywords_match = compute_keywords_match(cv_text, job_keywords) * 100
    normalized_exp = min(exp_years / 10.0, 1.0) * 100

    score = (
        tech_skills_match * 0.40 +
        normalized_exp * 0.30 +
        keywords_match * 0.30
    )

    return {
        "score": round(min(score, 100), 2),
        "skills": skills,
        "experience_years": round(exp_years, 1),
        "tech_skills_match": round(tech_skills_match, 2),
        "keywords_match": round(keywords_match, 2),
        "experience_score": round(normalized_exp, 2),
    }
