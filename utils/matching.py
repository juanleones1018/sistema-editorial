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
def calculate_specialization_bonus(

    full_query,

    research_topic,

    publications
):

    query = full_query.lower()

    corpus = (

        str(research_topic)

        +

        " "

        +

        str(publications)

    ).lower()

    keywords = [

        word.strip()

        for word in re.findall(

            r"\b[a-záéíóúñ]{5,}\b",

            query
        )
    ]

    keywords = list(

        set(keywords)
    )

    matches = 0

    for keyword in keywords:

        if keyword in corpus:

            matches += 1

    bonus = min(

        matches * 3,

        15
    )

    return bonus
