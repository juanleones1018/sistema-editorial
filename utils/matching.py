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

    if not query_keywords:

        return 0

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
        
        elif fuzz.partial_ratio(
        
                keyword,
        
                corpus
        
             ) >= 90:
        
            matches += 1

    # =========================
    # SCORE 0–100
    # =========================

    specialization_score = min(

        matches * 30,
    
        100
    )

    return round(

        specialization_score,

        1
    )


# =========================
# MATCHING GENERAL
# =========================

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

    # =========================
    # AFINIDAD TEMÁTICA
    # =========================

    topic_score = fuzz.token_set_ratio(

        full_query,

        topic
    )

    # =========================
    # PUBLICACIONES
    # =========================

    publication_score = fuzz.token_set_ratio(

        full_query,

        publications
    )

    # =========================
    # ESPECIALIZACIÓN
    # =========================

    specialization_score = (

        calculate_specialization_score(

            keywords,

            topic,

            publications
        )
    )

    # =========================
    # NORMALIZAR PESOS
    # =========================

    total = (

        thematic_weight

        +

        publication_weight
    )

    if total == 0:

        thematic_ratio = 0.5

        publication_ratio = 0.5

    else:

        thematic_ratio = (

            thematic_weight

            /

            total
        )

        publication_ratio = (

            publication_weight

            /

            total
        )

    # =========================
    # SCORE BASE
    # =========================

    fuzzy_score = (

        topic_score

        *

        thematic_ratio

        +

        publication_score

        *

        publication_ratio
    )

    # =========================
    # SCORE FINAL
    # =========================

    final_score = (

        fuzzy_score

        * 0.50

        +

        specialization_score

        * 0.50
    )

    final_score = min(

        final_score,

        100
    )

    return round(

        final_score,

        1
    )
