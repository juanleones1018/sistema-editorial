import re
import unicodedata

from rapidfuzz import fuzz


def normalize_text(text: str) -> str:
    text = str(text or "").strip().lower()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def tokenize_text(text: str) -> list[str]:
    return [
        token for token in normalize_text(text).split(" ")
        if token
    ]


def parse_keyword_list(raw_keywords: str) -> list[str]:
    raw = str(raw_keywords or "").strip()
    if not raw:
        return []

    keywords = [
        keyword.strip()
        for keyword in re.split(r"[\n;,]+", raw)
        if keyword.strip()
    ]

    if len(keywords) == 1 and " " in keywords[0]:
        candidate = re.sub(
            r"(?<=[0-9a-záéíóúñü])(?=[A-ZÁÉÍÓÚÑÜ])",
            "|||",
            keywords[0],
        )
        split_candidate = [
            keyword.strip()
            for keyword in re.split(r"\|\|\||[\n;,]+", candidate)
            if keyword.strip()
        ]
        if len(split_candidate) > 1:
            keywords = split_candidate

    return list(dict.fromkeys(keywords))


def calculate_specialization_score(
    keywords,
    priority_keywords,
    topic,
    publications,
    academic_profile="",
    department="",
    institution="",
):
    """Mide la cobertura de las palabras clave solicitadas."""
    query_keywords = [
        normalize_text(keyword)
        for keyword in parse_keyword_list(keywords)
        if normalize_text(keyword)
    ]

    if not query_keywords:
        return 0.0

    priority_values = priority_keywords or []
    if isinstance(priority_values, str):
        priority_values = parse_keyword_list(priority_values)

    priority_set = {
        normalize_text(str(keyword))
        for keyword in priority_values
        if normalize_text(str(keyword))
    }
    corpus = " ".join(
        normalize_text(value)
        for value in (topic, publications, academic_profile, department, institution)
    )

    if not corpus:
        return 0.0

    matches = 0
    possible = 0
    for keyword in query_keywords:
        weight = 4 if keyword in priority_set else 1
        possible += weight

        if keyword in corpus:
            matches += weight
            continue

        if fuzz.partial_ratio(keyword, corpus) >= 90:
            matches += weight
            continue

        keyword_tokens = tokenize_text(keyword)
        corpus_tokens = set(tokenize_text(corpus))
        if keyword_tokens and all(token in corpus_tokens for token in keyword_tokens):
            matches += weight

    return round((matches / possible) * 100, 1) if possible else 0.0


def _activity_score(status):
    return {
        "🟢 Activo": 100,
        "🟡 Verificar": 60,
        "⚪ Sin verificar": 25,
        "🔴 Inactivo": 0,
    }.get(str(status or "").strip(), 25)


def _evidence_score(source):
    source = normalize_text(source)

    if source in {"orcid", "openalex", "crossref", "google scholar"}:
        return 100
    if source in {"universidad", "validacion manual", "validación manual", "editorial"}:
        return 60
    return 0


def calculate_match_score(
    row,
    full_query,
    keywords,
    priority_keywords,
    thematic_weight,
    publication_weight,
    activity_weight=0,
    evidence_weight=0,
    status="⚪ Sin verificar",
    evidence_source="Sin evidencia",
):
    """Calcula un puntaje de 0 a 100 usando todos los pesos del formulario."""
    full_query = normalize_text(full_query)
    topic = normalize_text(row.get("research_topic", ""))
    publications = normalize_text(row.get("publications", ""))
    academic_profile = normalize_text(
        row.get("academic_degree", row.get("academic_profile", ""))
    )

    if not any((topic, publications, academic_profile)):
        return 0.0

    thematic_corpus = " ".join((topic, academic_profile, normalize_text(row.get("department", "")))).strip()
    fuzzy_thematic_score = (
        fuzz.token_set_ratio(full_query, thematic_corpus)
        if full_query and thematic_corpus else 0
    )
    specialization_score = calculate_specialization_score(
        keywords,
        priority_keywords,
        topic,
        publications,
        academic_profile,
        normalize_text(row.get("department", "")),
        normalize_text(row.get("institution", "")),
    )
    thematic_score = (
        (fuzzy_thematic_score * 0.55) + (specialization_score * 0.45)
        if keywords else fuzzy_thematic_score
    )

    publication_score = 0
    if publications:
        publication_score = fuzz.token_set_ratio(full_query, publications)
        if keywords:
            publication_score = max(
                publication_score,
                calculate_specialization_score(keywords, priority_keywords, "", publications, ""),
            )

    weights = {
        "thematic": max(0, thematic_weight),
        "publication": max(0, publication_weight),
        "activity": max(0, activity_weight),
        "evidence": max(0, evidence_weight),
    }
    total_weight = sum(weights.values())

    if not total_weight:
        return 0.0

    score = (
        thematic_score * weights["thematic"]
        + publication_score * weights["publication"]
        + _activity_score(status) * weights["activity"]
        + _evidence_score(evidence_source) * weights["evidence"]
    ) / total_weight

    return round(min(score, 100), 1)
