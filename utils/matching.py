import re

from rapidfuzz import fuzz


# =========================
# ESPECIALIZACIÓN TEMÁTICA
# =========================

def calculate_specialization_score(

    keywords,
    topic,
    publications,
    academic_profile=""
):

    if not keywords:

        return 0

    query_keywords = [

        keyword.strip().lower()

        for keyword in keywords.split(",")

        if keyword.strip()
    ]

    if not query_keywords:

        return 0

    corpus = (

        str(topic)

        +

        " "

        +

        str(publications)

        +

        " "

        +

        str(academic_profile)

    ).lower().strip()

    if not corpus:

        return 0

    matches = 0
    max_possible = 0

    GENERAL_TERMS = {

    "historia",
    "historia de colombia",
    "ciencia política",
    "ciencias políticas",
    "derecho",
    "economía",
    "educación",
    "políticas públicas",
    "america latina",
    "américa latina",
    "juventud",
    "salud",
    "género",
    "democracia",
    "participación"

    }

    for keyword in query_keywords:

        keyword = keyword.strip().lower()

        if not keyword:

            continue

        words = len(

            keyword.split()
        )

        # =========================
        # PESO SEGÚN ESPECIFICIDAD
        # =========================

        if words >= 4:

            weight = 4

        elif words == 3:

            weight = 3

        elif words == 2:

            weight = 2

        else:

            weight = 1

        # =========================
        # PENALIZAR TÉRMINOS GENERALES
        # =========================

        if keyword in GENERAL_TERMS:

            weight *= 0.5

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

    ).strip()

    publications = str(

        row.get(

            "publications",

            ""

        )

    ).strip()

    academic_profile = str(

        row.get(

            "academic_profile",

            ""

        )

    ).strip()

    # =========================
    # EVITAR PERFILES VACÍOS
    # =========================

    if (

        not topic

        and

        not publications

        and

        not academic_profile

    ):

        return 0

    corpus = (

        topic

        + " "

        + publications

        + " "

        + academic_profile

    )

    # =========================
    # AFINIDAD TEMÁTICA
    # =========================

    topic_score = fuzz.token_set_ratio(

        full_query,

        corpus
    )

    # =========================
    # PUBLICACIONES
    # =========================

    publication_score = fuzz.token_set_ratio(

        full_query,

        publications
    ) if publications else 0

    # =========================
    # ESPECIALIZACIÓN
    # =========================

    specialization_score = (

        calculate_specialization_score(

            keywords,

            topic,

            publications,

            academic_profile
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

        * 0.60

        +

        specialization_score

        * 0.40
    )

    final_score = min(

        final_score,

        100
    )

    return round(

        final_score,

        1
    )
