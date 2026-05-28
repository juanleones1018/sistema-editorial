import pandas as pd

from utils.db import supabase

# =========================
# CARGAR REVIEWERS
# =========================

def load_reviewers():

    all_data = []

    page_size = 1000

    start = 0

    while True:

        response = supabase.table(
            "reviewers"
        ).select("*").range(
            start,
            start + page_size - 1
        ).execute()

        data = response.data

        if not data:

            break

        all_data.extend(data)

        start += page_size

    return pd.DataFrame(all_data)
# =========================
# ACTUALIZAR REVIEWER
# =========================

def update_reviewer(

    reviewer_id,

    updated_data
):

    response = (

        supabase.table(
            "reviewers"
        )

        .update(
            updated_data
        )

        .eq(
            "id",
            reviewer_id
        )

        .execute()
    )

    return response
# =========================
# INSERTAR ACTIVIDAD
# =========================

def insert_activity(

    reviewer_id,

    is_active,

    source,

    notes,

    checked_by="Juan"
):

    response = (

        supabase.table(
            "reviewer_activity"
        )

        .insert({

            "reviewer_id":
                reviewer_id,

            "is_active":
                is_active,

            "source":
                source,

            "notes":
                notes,

            "checked_by":
                checked_by
        })

        .execute()
    )

    return response