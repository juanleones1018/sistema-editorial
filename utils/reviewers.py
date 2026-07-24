import re
import time

import httpx
import pandas as pd

from utils.db import get_supabase


EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PAGE_SIZE = 1000


def normalize_email(email):
    return str(email or "").strip().lower()


def validate_email(email):
    normalized = normalize_email(email)

    if not EMAIL_PATTERN.match(normalized):
        raise ValueError("Ingrese un correo electrónico válido.")

    return normalized


def _execute_with_retry(query):
    for attempt in range(3):
        try:
            return query.execute()
        except httpx.HTTPError as error:
            if attempt == 2:
                raise
            time.sleep(2 ** attempt)


def load_reviewer_statuses():
    """Devuelve el último estado de cada evaluador, incluso con más de 1000 filas."""
    activities = []
    start = 0

    while True:
        supabase = get_supabase()
        response = _execute_with_retry(
            supabase
            .table("reviewer_activity")
            .select("reviewer_id,is_active,source,notes,checked_by,checked_at")
            .order("checked_at", desc=True)
            .range(start, start + PAGE_SIZE - 1)
        )
        page = response.data

        if not page:
            break

        activities.extend(page)
        start += PAGE_SIZE

    status_dict = {}
    for activity in activities:
        reviewer_id = activity["reviewer_id"]
        if reviewer_id in status_dict:
            continue

        if activity.get("is_active"):
            status = "🟢 Activo"
        else:
            notes = str(activity.get("notes", ""))
            checked_by = str(activity.get("checked_by", ""))

            if "Revisión editorial" in notes or "Sugerencia editorial" in notes or checked_by == "BOT":
                status = "🟡 Verificar"
            elif "No disponible" in notes:
                status = "🔴 Inactivo"
            else:
                status = "⚪ Sin verificar"

        status_dict[reviewer_id] = (status, activity.get("source", "Sin evidencia"))

    return status_dict


def load_reviewers():
    """Carga los campos necesarios para matching y edición."""
    all_data = []
    start = 0
    select_columns = (
        "id,country,institution,full_name,email,department,academic_degree_level,"
        "academic_degree,publications,last_publication_year,profile_link,research_topic"
    )

    while True:
        supabase = get_supabase()
        response = _execute_with_retry(
            supabase
            .table("reviewers")
            .select(select_columns)
            .order("id")
            .range(start, start + PAGE_SIZE - 1)
        )
        data = response.data

        if not data:
            break

        all_data.extend(data)
        start += PAGE_SIZE

    return pd.DataFrame(all_data)


def load_activity(reviewer_id):
    response = (
        get_supabase().table("reviewer_activity")
        .select("*")
        .eq("reviewer_id", reviewer_id)
        .order("checked_at", desc=True)
        .execute()
    )
    return pd.DataFrame(response.data)


def get_reviewer_status(reviewer_id):
    return load_reviewer_statuses().get(
        reviewer_id,
        ("⚪ Sin verificar", "Sin evidencia"),
    )


def _find_reviewer_by_email(email):
    return (
        get_supabase().table("reviewers")
        .select("id")
        .ilike("email", email)
        .limit(1)
        .execute()
    )


def update_reviewer(reviewer_id, updated_data):
    updated_data = dict(updated_data)
    email = validate_email(updated_data.get("email"))
    existing = _find_reviewer_by_email(email)

    if existing.data and str(existing.data[0]["id"]) != str(reviewer_id):
        raise ValueError("Ese correo ya pertenece a otro evaluador.")

    updated_data["email"] = email
    return (
        get_supabase().table("reviewers")
        .update(updated_data)
        .eq("id", reviewer_id)
        .execute()
    )


def insert_reviewer(data):
    """Crea un evaluador o actualiza el existente con el mismo correo."""
    data = dict(data)
    email = validate_email(data.get("email"))
    data["email"] = email
    existing = _find_reviewer_by_email(email)

    if existing.data:
        return (
            get_supabase().table("reviewers")
            .update(data)
            .eq("id", existing.data[0]["id"])
            .execute()
        )

    return get_supabase().table("reviewers").insert(data).execute()


def insert_activity(data):
    """No crea dos registros consecutivos con exactamente el mismo estado."""
    data = dict(data)
    latest = (
        get_supabase().table("reviewer_activity")
        .select("*")
        .eq("reviewer_id", data["reviewer_id"])
        .order("checked_at", desc=True)
        .limit(1)
        .execute()
    )

    if latest.data:
        previous = latest.data[0]
        fields = ("is_active", "source", "notes", "checked_by")
        if all(previous.get(field) == data.get(field) for field in fields):
            return latest

    return get_supabase().table("reviewer_activity").insert(data).execute()


def update_reviewer_activity(reviewer_id, is_active, source, notes, checked_by="BOT"):
    return insert_activity({
        "reviewer_id": reviewer_id,
        "is_active": is_active,
        "source": source,
        "notes": notes,
        "checked_by": checked_by,
    })


def set_reviewer_status(reviewer_id, is_active, source, notes):
    return update_reviewer_activity(
        reviewer_id=reviewer_id,
        is_active=is_active,
        source=source,
        notes=notes,
        checked_by="Editorial",
    )
