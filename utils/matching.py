import re

from rapidfuzz import fuzz
# =========================
# ESPECIALIZACIÓN TEMÁTICA
# =========================

def calculate_specialization_score(

    full_query,

    topic,

    publications
):

    STOPWORDS = {

        "artículo",
        "investigación",
        "análisis",
        "sociales",
        "desarrollo",
        "sistema",
        "proyecto",
        "colombia",
        "estado",
        "guerra",
        "política"
    }

    keywords = re.findall(

        r"\b[a-záéíóúñ]{7,}\b",

        full_query.lower()
    )

    keywords = [

        keyword

        for keyword in set(keywords)

        if keyword not in STOPWORDS
    ]

    corpus = (

        topic

        +

        " "

        +

        publications

    ).lower()

    matches = 0

    for keyword in keywords:

        if keyword in corpus:

            matches += 1

    return min(

        matches * 10,

        100
    )

def calculate_match_score(
    row,
    full_query,
    specialization_query,
    thematic_weight,
    publication_weight
):

    topic = str(
        row.get(
            "research_topic",
            ""
        )
    )

    publications = str(
        row.get(
            "publications",
            ""
        )
    )

    # =========================
    # AFINIDAD GENERAL
    # =========================

    topic_score = fuzz.token_set_ratio(

        full_query,

        topic
    )

    publication_score = max(

        fuzz.token_set_ratio(

            full_query,
    
            publications
        ),
    
        fuzz.partial_ratio(
    
            specialization_query,
    
            publications
        )
    )
    # =========================
    # ESPECIALIZACIÓN
    # =========================

    specialization_score = (

        calculate_specialization_score(

            specialization_query,

            topic,

            publications
        )
    )

    # =========================
    # SCORE FINAL
    # =========================

    final_score = (

        (
            topic_score
            *
            thematic_weight
        )

        +

        (
            publication_score
            *
            publication_weight
        )

    ) / 100

    # Bonus máximo de 15 puntos

    final_score += (

        specialization_score

        * 0.15
    )

    final_score = min(

        final_score,

        100
    )

    return round(

        final_score,

        1
    )
