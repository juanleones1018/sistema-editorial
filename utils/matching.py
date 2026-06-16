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

    STOPWORDS = {

        "historia",
        "colombia",
        "américa",
        "america",
        "latina",
        "estado",
        "guerra",
        "política",
        "politica",
        "sociedad",
        "social",
        "cultura",
        "desarrollo"

    }

    # =========================
    # NORMALIZAR KEYWORDS
    # =========================

    query_keywords = [

        keyword.strip().lower()

        for keyword in keywords.split(",")

        if keyword.strip()
    ]

    query_keywords = [

        keyword

        for keyword in query_keywords

        if keyword not in STOPWORDS
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
    max_possible = 0

    for keyword in query_keywords:

        keyword = keyword.strip()

        if not keyword:

            continue

        # =========================
        # PESO SEGÚN ESPECIFICIDAD
        # =========================

        words = len(

            keyword.split()
        )

        if words >= 4:

            weight = 4

        elif words == 3:

            weight = 3

        elif words == 2:

            weight = 2

        else:

            weight = 1

        max_possible += weight

        # =========================
        # MATCH EXACTO
        # =========================

        if keyword in corpus:

            matches += weight

            continue

        # =========================
        # MATCH DIFUSO
        # =========================

        similarity = fuzz.partial_ratio(

            keyword,

            corpus
        )

        if similarity >= 90:

            matches += weight

    # =========================
    # SCORE 0–100
    # =========================

    specialization_score = (

        matches

        /

        max_possible

    ) * 100

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

        * 0.30

        +

        specialization_score

        * 0.70
    )

    final_score = min(

        final_score,

        100
    )

    return round(

        final_score,

        1
    )
