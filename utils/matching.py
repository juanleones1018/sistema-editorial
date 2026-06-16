import re

from rapidfuzz import fuzz
# =========================
# ESPECIALIZACIÓN TEMÁTICA
# =========================

def calculate_specialization_score(

    keywords,
    topic,
    publications
):

    if not keywords:

        return 0

    # =========================
    # NORMALIZAR KEYWORDS
    # =========================

    query_keywords = [

        keyword.strip().lower()

        for keyword in keywords.split(",")

        if keyword.strip()
    ]

    # =========================
    # CORPUS DEL EVALUADOR
    # =========================

    corpus = (

        str(topic)

        +

        " "

        +

        str(publications)

    ).lower()

    # =========================
    # BUSCAR COINCIDENCIAS
    # =========================

    matches = 0

    for keyword in query_keywords:

        if keyword in corpus:

            matches += 1

    # =========================
    # SCORE 0–100
    # =========================

    specialization_score = (

        matches

        /

        len(query_keywords)

    ) * 100

    return round(

        specialization_score,

        1
    )

def calculate_match_score(

    row,
    full_query,
    keywords,
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

    topic_score = fuzz.token_set_ratio(

        full_query,

        topic
    )

    publication_score = fuzz.token_set_ratio(

        full_query,

        publications
    )

    specialization_score = (

        calculate_specialization_score(

            keywords,

            topic,

            publications
        )
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

    # Bonus editorial

    final_score += (

        specialization_score

        * 0.20
    )

    final_score = min(

        final_score,

        100
    )

    return round(

        final_score,

        1
    )
