import pandas as pd

from utils.db import supabase

# =========================
# CARGAR REVIEWERS
# =========================
def load_reviewer_statuses():

    response = supabase.table(
        "reviewer_activity"
    ).select(
        "*"
    ).order(
        "checked_at",
        desc=True
    ).execute()

    data = response.data

    if not data:

        return {}

    statuses = {}

    for item in data:

        reviewer_id = item["reviewer_id"]

        # Nos quedamos solo con el registro más reciente
        if reviewer_id not in statuses:

            statuses[reviewer_id] = (

                "🟢 Activo"
                if item["is_active"]
                else "🔴 Revisar",

                item["source"]
            )

    return statuses
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


def get_reviewer_status(
    reviewer_id
):

    try:

        activity = load_activity(
            reviewer_id
        )

        if activity.empty:

            return (
                "🟡 Sin verificar",
                None
            )

        latest = activity.iloc[0]

        if latest["is_active"]:

            return (
                "🟢 Activo",
                latest["source"]
            )

        return (
            "🔴 Inactivo",
            latest["source"]
        )

    except:

        return (
            "🟡 Verificar",
            None
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
from utils.db import supabase
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
def set_reviewer_status(
    reviewer_id,
    is_active,
    source,
    notes
):

    return supabase.table(
        "reviewer_activity"
    ).insert({

        "reviewer_id": reviewer_id,

        "is_active": is_active,

        "source": source,

        "notes": notes

    }).execute()
