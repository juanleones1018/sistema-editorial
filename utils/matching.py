import re

from rapidfuzz import fuzz


def calculate_match_score(
    row,
    full_query,
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
    # MATCH TEMÁTICO GENERAL
    # =========================

    topic_score = fuzz.token_set_ratio(

        full_query,

        topic
    )

    publication_score = fuzz.token_set_ratio(

        full_query,

        publications
    )

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

    # =========================
    # BONUS DE ESPECIALIZACIÓN
    # =========================

    STOPWORDS = {

        "artículo",
        "investigación",
        "análisis",
        "sociales",
        "política",
        "proyecto",
        "desarrollo",
        "sistema",
        "colombia",
        "estudio",
        "trabajo"
    }

    keywords = re.findall(

        r"\b[a-záéíóúñ]{5,}\b",

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

    specialization_bonus = min(

        matches * 3,

        15
    )

    final_score += specialization_bonus

    final_score = min(

        final_score,

        100
    )

    return round(
        final_score,
        1
    )
