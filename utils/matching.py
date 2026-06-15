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

    # ======================
    # SCORE TEMÁTICO
    # ======================

    topic_score = fuzz.token_set_ratio(

        full_query,

        topic
    )

    # ======================
    # SCORE PUBLICACIONES
    # ======================

    publication_score = fuzz.token_set_ratio(

        full_query,

        publications
    )

    # ======================
    # SCORE FINAL
    # ======================

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

    # ======================
    # BONUS ACTUALIDAD
    # ======================

    try:

        last_year = int(

            row.get(
                "last_publication_year",
                0
            )
        )

        if last_year >= 2022:

            final_score += 5

    except:

        pass

    return round(
        final_score,
        1
    )