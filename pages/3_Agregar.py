import streamlit as st
from utils.auth import (
    login
)

if not login():

    st.stop()
from utils.layout import (
    setup_page,
    render_sidebar
)

from utils.reviewers import (
    load_reviewers,
    insert_reviewer,
    insert_activity
)

# =========================
# CONFIG
# =========================

setup_page(
    "Agregar evaluador"
)

render_sidebar()

# =========================
# HEADER
# =========================

st.title(
    "➕ Agregar Evaluador"
)

st.caption(
    "Registro manual de nuevos pares evaluadores"
)

st.divider()

# =========================
# FORMULARIO
# =========================

with st.form(
    "add_reviewer_form"
):

    col1, col2 = st.columns(2)

    with col1:

        full_name = st.text_input(
            "Nombre completo *"
        )

        email = st.text_input(
            "Correo electrónico *"
        )

        country = st.text_input(
            "País"
        )

        institution = st.text_input(
            "Institución"
        )

        department = st.text_input(
            "Departamento"
        )

    with col2:

        academic_degree_level = st.selectbox(

            "Nivel académico",

            [
                "Doctorado",
                "Maestría",
                "Especialización",
                "Pregrado",
                "No definido"
            ]
        )

        last_publication_year = st.number_input(

            "Última publicación",

            min_value=1900,

            max_value=2100,

            value=2024
        )

        profile_link = st.text_input(
            "Perfil académico"
        )

        is_active = st.checkbox(
            "Activo",
            value=True
        )

    st.divider()

    academic_degree = st.text_area(
        "Grado académico completo"
    )

    research_topic = st.text_area(

        "Tema de investigación",

        height=150
    )

    publications = st.text_area(

        "Publicaciones",

        height=200
    )

    submitted = st.form_submit_button(
        "💾 Guardar evaluador"
    )

# =========================
# VALIDACIÓN
# =========================

if submitted:

    if not full_name:

        st.error(
            "Debe ingresar el nombre"
        )

    elif not email:

        st.error(
            "Debe ingresar el correo"
        )

    else:

        try:

            data = {

                "full_name":
                    full_name,

                "email":
                    email,

                "country":
                    country,

                "institution":
                    institution,

                "department":
                    department,

                "academic_degree":
                    academic_degree,

                "academic_degree_level":
                    academic_degree_level,

                "last_publication_year":
                    last_publication_year,

                "profile_link":
                    profile_link,

                "research_topic":
                    research_topic,

                "publications":
                    publications
            }

            # =========================
            # INSERT REVIEWER
            # =========================

            response = insert_reviewer(
                data
            )

            reviewer = (
                response.data[0]
            )

            reviewer_id = (
                reviewer["id"]
            )

            # =========================
            # INSERT ACTIVITY
            # =========================

            insert_activity({

                "reviewer_id":
                    reviewer_id,

                "is_active":
                    is_active,

                "source":
                    "Manual",

                "checked_by":
                    "Administrador",

                "notes":
                    "Creado desde formulario"
            })

            st.success(
                "✅ Evaluador agregado correctamente"
            )

        except Exception as e:

            st.error(
                f"Error: {e}"
            )
