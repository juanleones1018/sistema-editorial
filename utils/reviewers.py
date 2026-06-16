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
def load_activity(
    reviewer_id
):

    response = (

        supabase

        .table(
            "reviewer_activity"
        )

        .select("*")

        .eq(
            "reviewer_id",
            reviewer_id
        )

        .order(
            "checked_at",
            desc=True
        )

        .execute()
    )

    return pd.DataFrame(
        response.data
    )


def update_reviewer_activity(
    reviewer_id,
    is_active,
    source,
    notes,
    checked_by="BOT"
):

    data = {

        "reviewer_id": reviewer_id,

        "is_active": is_active,

        "source": source,

        "notes": notes,

        "checked_by": checked_by
    }

    return insert_activity(
        data
    )


def get_reviewer_status(reviewer_id):

    response = supabase.table(
        "reviewer_activity"
    ).select(
        "*"
    ).eq(
        "reviewer_id",
        reviewer_id
    ).order(
        "checked_at",
        desc=True
    ).limit(
        1
    ).execute()

    if not response.data:

        return (

            "⚪ Sin verificar",

            "Sin evidencia"
        )

    activity = response.data[0]

    if activity["is_active"]:

        return (

            "🟢 Activo",

            activity["source"]
        )

    notes = str(
        activity.get(
            "notes",
            ""
        )
    )

    checked_by = str(
        activity.get(
            "checked_by",
            ""
        )
    )

    if "🟡 Revisión editorial" in notes:

        return (

            "🟡 Verificar",

            activity["source"]
        )

    if (

        "Sugerencia editorial" in notes

        or

        checked_by == "BOT"
    ):

        return (

            "🟡 Verificar",

            activity["source"]
        )

    if "🔴 No disponible" in notes:

        return (

            "🔴 Inactivo",

            activity["source"]
        )

    # =========================
    # CASO POR DEFECTO
    # =========================

    return (

        "⚪ Sin verificar",

        activity["source"]
    )
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


def insert_activity(data):

    return (

        supabase

        .table(
            "reviewer_activity"
        )

        .insert(data)

        .execute()
    )

def insert_reviewer(data):

    response = (

        supabase

        .table("reviewers")

        .insert(data)

        .execute()
    )

    return response
