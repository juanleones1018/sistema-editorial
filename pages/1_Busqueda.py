import streamlit as st
import pandas as pd

from utils.reviewers import (
    load_reviewers,
    update_reviewer,
    insert_activity
)
from utils.layout import (

    setup_page,

    render_sidebar
)
setup_page(
    "Búsqueda"
)

render_sidebar()
# =========================
# CONFIG
# =========================

st.set_page_config(
    page_title="Gestión Evaluadores",
    layout="wide"
)

# =========================
# LOAD DATA
# =========================

@st.cache_data
def get_data():

    return load_reviewers()

df = get_data()

# =========================
# VALIDAR DATA
# =========================

if df.empty:

    st.warning(
        "No hay datos cargados"
    )

    st.stop()

# =========================
# LIMPIAR DATAFRAME
# =========================

df = df.fillna("")

string_columns = [

    "full_name",

    "country",

    "institution",

    "department",

    "academic_degree",

    "academic_degree_level",

    "research_topic",

    "publications",

    "profile_link"
]

for col in string_columns:

    if col in df.columns:

        df[col] = (

            df[col]
            .astype(str)
            .str.strip()
        )

# =========================
# HEADER
# =========================

st.title(
    "🔎 Gestión de Evaluadores"
)

st.caption(
    "Sistema editorial centralizado"
)

# =========================
# REFRESH
# =========================

if st.button(
    "🔄 Actualizar datos"
):

    st.cache_data.clear()

    st.rerun()

st.divider()

# =========================
# MÉTRICAS
# =========================

m1, m2, m3, m4 = st.columns(4)

with m1:

    st.metric(
        "Evaluadores",
        len(df)
    )

with m2:

    st.metric(
        "Países",
        df["country"].nunique()
    )

with m3:

    st.metric(
        "Instituciones",
        df["institution"].nunique()
    )

with m4:

    st.metric(
        "Departamentos",
        df["department"].nunique()
    )

st.divider()

# =========================
# FILTROS
# =========================

st.subheader(
    "Filtros"
)

f1, f2, f3, f4 = st.columns(4)

# =========================
# NOMBRE
# =========================

with f1:

    search_name = st.text_input(
        "Nombre"
    )

# =========================
# PAÍS
# =========================

with f2:

    countries = sorted(

        df["country"]
        .dropna()
        .unique()
    )

    selected_country = st.selectbox(

        "País",

        ["Todos"] + list(countries)
    )

# =========================
# FILTRAR UNIVERSIDADES
# =========================

filtered_institutions_df = df.copy()

if selected_country != "Todos":

    filtered_institutions_df = (

        filtered_institutions_df[

            filtered_institutions_df[
                "country"
            ]
            ==
            selected_country
        ]
    )

# =========================
# INSTITUCIÓN
# =========================

with f3:

    institutions = sorted(

        filtered_institutions_df[
            "institution"
        ]
        .dropna()
        .unique()
    )

    selected_institution = st.selectbox(

        "Institución",

        ["Todas"] + list(institutions)
    )

# =========================
# NIVEL ACADÉMICO
# =========================

with f4:

    selected_degree = st.selectbox(

        "Nivel académico",

        ["Todos"]

        +

        sorted(

            df[
                "academic_degree_level"
            ]
            .dropna()
            .unique()
        )
    )

st.divider()

# =========================
# FILTRAR DATAFRAME
# =========================

filtered_df = df.copy()

# =========================
# FILTRO NOMBRE
# =========================

if search_name:

    filtered_df = filtered_df[

        filtered_df[
            "full_name"
        ]
        .str.contains(

            search_name,

            case=False,

            na=False
        )
    ]

# =========================
# FILTRO PAÍS
# =========================

if selected_country != "Todos":

    filtered_df = filtered_df[

        filtered_df[
            "country"
        ]
        ==
        selected_country
    ]

# =========================
# FILTRO INSTITUCIÓN
# =========================

if selected_institution != "Todas":

    filtered_df = filtered_df[

        filtered_df[
            "institution"
        ]
        ==
        selected_institution
    ]

# =========================
# FILTRO NIVEL
# =========================

if selected_degree != "Todos":

    filtered_df = filtered_df[

        filtered_df[
            "academic_degree_level"
        ]
        ==
        selected_degree
    ]

# =========================
# VALIDAR RESULTADOS
# =========================

if filtered_df.empty:

    st.warning(
        "No hay resultados"
    )

    st.stop()

# =========================
# TABLA
# =========================

st.subheader(
    f"Resultados ({len(filtered_df)})"
)

table_df = filtered_df[[

    "full_name",

    "country",

    "institution",

    "academic_degree_level",

    "last_publication_year"
]].copy()

table_df.columns = [

    "Nombre",

    "País",

    "Institución",

    "Nivel",

    "Última publicación"
]

st.dataframe(

    table_df,

    use_container_width=True,

    height=450
)

st.divider()

# =========================
# SELECTOR
# =========================

filtered_df = filtered_df.reset_index(
    drop=True
)

filtered_df["selector"] = (

    filtered_df.index.astype(str)

    +

    " - "

    +

    filtered_df["full_name"]

    +

    " | "

    +

    filtered_df["institution"]
)

selected_option = st.selectbox(

    "Seleccionar evaluador",

    filtered_df["selector"],

    key="reviewer_selector"
)

selected_index = int(

    selected_option.split(
        " - "
    )[0]
)

selected = filtered_df.iloc[
    selected_index
]

st.divider()

# =========================
# FORMULARIO
# =========================


st.subheader(
    "✏️ Editar evaluador"
)

with st.form(
    "edit_reviewer_form"
):

    # =========================
    # DATOS PRINCIPALES
    # =========================

    c1, c2 = st.columns(2)

    with c1:

        full_name = st.text_input(

            "Nombre",

            value=selected[
                "full_name"
            ],

            key=f"name_{selected['id']}"
        )

        email = st.text_input(

            "Correo",

            value=selected[
                "email"
            ],

            key=f"email_{selected['id']}"
        )

        country = st.text_input(

            "País",

            value=selected[
                "country"
            ],

            key=f"country_{selected['id']}"
        )

        institution = st.text_input(

            "Institución",

            value=selected[
                "institution"
            ],

            key=f"institution_{selected['id']}"
        )

    with c2:

        department = st.text_input(

            "Departamento",

            value=selected[
                "department"
            ],

            key=f"department_{selected['id']}"
        )

        academic_degree = st.text_input(

            "Grado académico",

            value=selected[
                "academic_degree"
            ],

            key=f"degree_{selected['id']}"
        )

        # =========================
        # NIVEL ACADÉMICO
        # =========================

        degree_options = [

            "Doctorado",

            "Maestría",

            "Especialización",

            "Pregrado",

            "No definido"
        ]

        current_degree = selected[
            "academic_degree_level"
        ]

        if current_degree not in degree_options:

            current_degree = "No definido"

        academic_degree_level = (
            st.selectbox(

                "Nivel académico",

                degree_options,

                index=degree_options.index(
                    current_degree
                ),

                key=f"degree_level_{selected['id']}"
            )
        )

        last_publication_year = (
            st.number_input(

                "Última publicación",

                value=int(

                    selected[
                        "last_publication_year"
                    ]

                    or 0
                ),

                step=1,

                key=f"year_{selected['id']}"
            )
        )

    # =========================
    # PERFIL
    # =========================

    profile_link = st.text_input(

        "Perfil académico",

        value=selected[
            "profile_link"
        ],

        key=f"profile_{selected['id']}"
    )

    # =========================
    # TEMA
    # =========================

    research_topic = st.text_area(

        "Tema investigación",

        value=selected[
            "research_topic"
        ],

        height=150,

        key=f"topic_{selected['id']}"
    )

    # =========================
    # PUBLICACIONES
    # =========================

    publications = st.text_area(

        "Publicaciones",

        value=selected[
            "publications"
        ],

        height=250,

        key=f"publications_{selected['id']}"
    )

    st.divider()

    # =========================
    # ESTADO EDITORIAL
    # =========================

    st.subheader(
        "📌 Estado editorial"
    )

    editorial_col1, editorial_col2 = (
        st.columns(2)
    )

    with editorial_col1:

        activity_status = st.selectbox(

            "Estado",

            [

                "Activo",

                "Inactivo",

                "Fallecido",

                "Pendiente"
            ],

            key=f"activity_{selected['id']}"
        )

    with editorial_col2:

        validation_source = st.selectbox(

            "Fuente validación",

            [

                "Validación manual",

                "ORCID",

                "Google Scholar",

                "OpenAlex",

                "Universidad",

                "Otro"
            ],

            key=f"source_{selected['id']}"
        )

    activity_notes = st.text_area(

        "Notas editoriales",

        height=120,

        key=f"notes_{selected['id']}"
    )

    st.divider()

    # =========================
    # BOTONES
    # =========================

    b1, b2 = st.columns(2)

    with b1:

        submitted = st.form_submit_button(
            "💾 Guardar cambios"
        )

    with b2:

        save_activity = (
            st.form_submit_button(
                "📌 Guardar validación"
            )
        )

    # =========================
    # UPDATE REVIEWER
    # =========================

    if submitted:

        updated_data = {

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

        update_reviewer(

            selected["id"],

            updated_data
        )

        st.success(
            "✅ Evaluador actualizado"
        )

        st.cache_data.clear()

        st.rerun()

    # =========================
    # INSERT ACTIVITY
    # =========================

    if save_activity:

        is_active = (
            activity_status
            ==
            "Activo"
        )

        insert_activity(

            reviewer_id=selected["id"],

            is_active=is_active,

            source=validation_source,

            notes=activity_notes
        )

        st.success(
            "📌 Validación editorial guardada"
        )

        st.rerun()

