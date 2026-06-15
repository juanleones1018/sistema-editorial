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

    return round(
        final_score,
        1
    )
