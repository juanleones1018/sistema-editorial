import streamlit as st

st.set_page_config(
    page_title="Matching",
    layout="wide",
    initial_sidebar_state="expanded",
)

import pandas as pd
from utils.auth import (
    login
)

if not login():
    st.stop()
from utils.matching import (
    calculate_match_score,
    parse_keyword_list,
)
from utils.reviewers import (

    load_reviewers,

    load_reviewer_statuses,

    get_reviewer_status,
    set_reviewer_status,
    update_reviewer,

)
from utils.layout import (

    setup_page,

    render_sidebar
)


def format_publications_for_display(publications_value):
    """Devuelve una lista de publicaciones legible para mostrar en la UI."""

    if publications_value is None:
        return []

    if isinstance(publications_value, list):
        entries = [str(item).strip() for item in publications_value if str(item).strip()]
        return entries

    text = str(publications_value).strip()

    if not text:
        return []

    entries = [item.strip() for item in text.splitlines() if item.strip()]

    if len(entries) == 1:
        candidate = entries[0]
        if ";" in candidate:
            entries = [item.strip() for item in candidate.split(";") if item.strip()]

    return entries


setup_page(
    "Búsqueda"
)

render_sidebar()
# =========================
# CONFIG
# =========================

# =========================
# LOAD DATA
# =========================

@st.cache_data(ttl=3600)
def get_data():
    return load_reviewers()

@st.cache_data(ttl=3600)
def get_statuses():
    return load_reviewer_statuses()

# =========================
# HEADER
# =========================

st.title(
    "🎯 Matching de Evaluadores"
)

st.caption(
    "Sistema heurístico de afinidad temática"
)

st.divider()

# =========================
# LAYOUT
# =========================

left, right = st.columns([3, 1])

# =========================
# PANEL IZQUIERDO
# =========================

with left:

    st.subheader(
        "📄 Definir artículo / tema"
    )

    with st.form("matching_form"):

        title = st.text_input(
            "Título artículo",
            key="matching_title"
        )

        query = st.text_area(
            "Resumen / descripción",
            height=220,
            placeholder="""
Describe el artículo, tema o enfoque de investigación...
""",
            key="matching_query"
        )

        keywords = st.text_input(
            "Palabras clave separadas por coma o punto y coma",
            placeholder="Regeneración, Constitución de 1886, Guerra de los Mil Días",
            key="matching_keywords"
        )
        st.caption(
            "Puedes usar comas, punto y coma o saltos de línea. Si no usas separadores, el sistema intentará dividir términos cuando detecte mayúsculas unidas."
        )

        keyword_options = parse_keyword_list(keywords)

        priority_keywords = st.multiselect(
            "🎯 Palabras clave prioritarias",
            options=keyword_options,
            default=[],
            key="matching_priority_keywords"
        )

        search_submitted = st.form_submit_button("Buscar evaluadores")

    full_query = " ".join((title, query, keywords)).strip()

# =========================
# PANEL DERECHO
# =========================

with right:

    st.subheader(
        "⚙️ Configuración"
    )

    if st.button("Actualizar datos", key="refresh_matching"):
        get_data.clear()
        get_statuses.clear()
        st.rerun()

    with st.spinner("Cargando datos de evaluadores..."):
        df = get_data()

    with st.spinner("Cargando estados de actividad de evaluadores..."):
        status_dict = get_statuses()

    if df.empty:
        st.warning(
            "No hay evaluadores"
        )
        st.stop()

    df = df.fillna("")

    countries = sorted(
        df["country"]
        .dropna()
        .unique()
    )
    only_active = st.checkbox(
    
            "Solo evaluadores activos",
        
            value=True
    )

    selected_country = st.selectbox(

        "País",

        ["Todos"] + list(countries)
    )

    degree_options = [

        "Todos",

        "Doctorado",

        "Maestría",

        "Especialización",

        "Pregrado"
    ]

    selected_degree = st.selectbox(

        "Nivel mínimo",

        degree_options
    )

    st.divider()

    st.markdown(
        "### 🎯 Presets editoriales"
    )
    
    preset = st.selectbox(
    
        "Selecciona una estrategia",
    
        [
    
            "Personalizado",
    
            "⚖️ Equilibrado",
    
            "🎓 Especialista",
    
            "⚡ Disponibilidad",
    
            "📚 Trayectoria académica"
    
        ]
    )
    
    # =========================
    # PESOS
    # =========================
    
    if preset == "⚖️ Equilibrado":
    
        thematic_weight = 60
        publication_weight = 20
        activity_weight = 10
        evidence_weight = 10
    
    elif preset == "🎓 Especialista":
    
        thematic_weight = 80
        publication_weight = 10
        activity_weight = 5
        evidence_weight = 5
    
    elif preset == "⚡ Disponibilidad":
    
        thematic_weight = 40
        publication_weight = 20
        activity_weight = 25
        evidence_weight = 15
    
    elif preset == "📚 Trayectoria académica":
    
        thematic_weight = 50
        publication_weight = 35
        activity_weight = 5
        evidence_weight = 10
    
    else:
    
        st.markdown(
            "### 📊 Criterios"
        )
    
        thematic_weight = st.slider(
    
            "Afinidad temática",
    
            0,
    
            100,
    
            60
        )
    
        publication_weight = st.slider(
    
            "Publicaciones",
    
            0,
    
            100,
    
            20
        )
    
        activity_weight = st.slider(
    
            "Actividad reciente",
    
            0,
    
            100,
    
            10
        )
    
        evidence_weight = st.slider(
    
            "Evidencia automática",
    
            0,
    
            100,
    
            10
        )
        
    total_weight = (
        
            thematic_weight
        
            +
        
            publication_weight
        
            +
        
            activity_weight
        
            +
        
            evidence_weight
        )
    if total_weight != 100:
        
            st.error(
        
                f"""
        Los criterios deben sumar exactamente 100%.
        
        Actualmente suman {total_weight}%.
        """
            )
        
    else:
        
            st.success(
                "✅ Configuración válida"
            )
    st.info(
            f"""
        📊 Configuración actual:
        
        • Afinidad temática: {thematic_weight}%
        
        • Publicaciones: {publication_weight}%
        
        • Actividad reciente: {activity_weight}%
        
        • Evidencia automática: {evidence_weight}%
        """
        )
    st.divider()

    st.info(
            f"""
    🔎 Evaluadores cargados:
    {len(df)}
    
    🌎 Países:
    {df['country'].nunique()}
    
    🏛 Instituciones:
    {df['institution'].nunique()}
    """
        )
    
    st.divider()

# =========================
# FILTRAR
# =========================

filtered_df = df.copy()

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
if only_active:

    eligible_ids = [

        reviewer_id

        for reviewer_id, (
            status,
            _
        ) in status_dict.items()

        if status == "🟢 Activo"
    ]

    filtered_df = filtered_df[

        filtered_df["id"].isin(
            eligible_ids
        )
    ]

# =========================
# QUERY FINAL
# =========================

full_query = (

    f"{title} "

    f"{query} "

    f"{keywords}"
)

specialization_query = keywords
# =========================
# MATCHING
# =========================

if full_query.strip() and total_weight == 100:

    scores = []

    for _, row in filtered_df.iterrows():

        topic = str(
            row.get(
                "research_topic",
                ""
            )
        )

        status, source = status_dict.get(

            row["id"],
        
            (
                "⚪ Sin verificar",
                "Sin evidencia"
            )
        )

        final_score = calculate_match_score(

            row,

            full_query,
            keywords,
            priority_keywords,

            thematic_weight,

            publication_weight,

            activity_weight,

            evidence_weight,

            status,

            source,
        )

        # =========================
        # NORMALIZAR ÚLTIMA PUBLICACIÓN
        # =========================

        last_year = row.get(

            "last_publication_year",

            None
        )

        if pd.isna(last_year) or last_year == "":

            last_year = "N/D"

        else:

            last_year = str(

                int(last_year)
            )

        scores.append({
            "ID":
                row["id"],
            "Nombre":
                row["full_name"],

            "Correo":
                row["email"],

            "Institución":
                row["institution"],

            "País":
                row["country"],

            "Grado":
                row.get(
                    "academic_degree_level",
                    "No disponible"
                ),
            
            "Formación":
                row.get(
                    "academic_degree",
                    "No disponible"
                ),
            
            "Publicaciones":
                row.get(
                    "publications",
                    "No disponible"
                ),
            "Última publicación":
                last_year,

            "Score":
                round(
                    final_score,
                    1
                ),

            "Tema":
                topic[:300],

            "Estado":
                status,

            "Fuente":
                source
        })

    # =========================
    # RESULTADOS
    # =========================

    results_df = pd.DataFrame(
        scores
    )

    if results_df.empty:

        st.warning(
            "No se encontraron evaluadores con los criterios seleccionados."
        )

    else:

        results_df = results_df.sort_values(

            by="Score",

            ascending=False
        )

        results_df = results_df.head(30)

        st.subheader(
            "🏆 Mejores coincidencias"
        )

        for idx, row in results_df.iterrows():

            with st.container():
 
                top, bottom = st.columns([5, 1])
 
                with top:
 
                    st.markdown(
                        f"### 👨‍🏫 {row['Nombre']}"
                    )
 
                    st.caption(
                        f"""
                🏛 {row['Institución']} • 🌎 {row['País']}
 
                {row['Estado']}
                """
                    )

                    with st.expander("Editar datos del evaluador", expanded=False):
                        full_name = st.text_input(
                            "Nombre",
                            value=row["Nombre"],
                            key=f"name_{row['ID']}"
                        )
                        email = st.text_input(
                            "Correo",
                            value=row["Correo"],
                            key=f"email_{row['ID']}"
                        )
                        institution = st.text_input(
                            "Institución",
                            value=row["Institución"],
                            key=f"institution_{row['ID']}"
                        )
                        country = st.text_input(
                            "País",
                            value=row["País"],
                            key=f"country_{row['ID']}"
                        )
                        degree = st.text_input(
                            "Grado",
                            value=row["Grado"],
                            key=f"degree_{row['ID']}"
                        )
                        formation = st.text_input(
                            "Formación",
                            value=row["Formación"],
                            key=f"formation_{row['ID']}"
                        )
                        publications = st.text_area(
                            "Publicaciones",
                            value=row["Publicaciones"],
                            height=180,
                            key=f"publications_{row['ID']}"
                        )
                        research_topic = st.text_area(
                            "Tema",
                            value=row["Tema"],
                            height=180,
                            key=f"topic_{row['ID']}"
                        )
                        save_reviewer = st.button(
                            "Guardar cambios",
                            key=f"save_reviewer_{row['ID']}"
                        )

                        if save_reviewer:
                            updated_data = {
                                "full_name": full_name,
                                "email": email,
                                "institution": institution,
                                "country": country,
                                "academic_degree_level": degree,
                                "academic_degree": formation,
                                "publications": publications,
                                "research_topic": research_topic,
                            }
                            update_reviewer(row["ID"], updated_data)
                            get_data.clear()
                            st.success("Cambios guardados")
                            st.rerun()

                    new_status = st.selectbox(
                        "Actualizar estado",
                        [
                            "Sin cambios",
                            "Activo",
                            "Revisión editorial",
                            "No disponible"
                        ],
                        key=f"status_{row['ID']}"
                    )
                    if st.button(
                        "Guardar",
                        key=f"save_{row['ID']}"
                    ):
                        if new_status != "Sin cambios":
                            notes = (
                                f"Actualizado desde Matching: "
                                f"{new_status}"
                            )
                            is_active = new_status == "Activo"
                            set_reviewer_status(
                                reviewer_id=row["ID"],
                                is_active=is_active,
                                source="Editorial",
                                notes=notes
                            )
                            get_statuses.clear()
                            st.success(
                                "Estado actualizado."
                            )
                            st.rerun()
                    st.code(
                        row["Correo"]
                    )
 
                badge1, badge2, badge3 = st.columns(3)

                with badge1:
                    st.success(
                        f"🎓 {row['Grado']}"
                    )

                with badge2:
                    st.info(
                        f"📅 {row['Última publicación']}"
                    )

                with badge3:
                    if row["Score"] >= 70:
                        st.success(
                            "⭐ Alta afinidad"
                        )
                    elif row["Score"] >= 50:
                        st.warning(
                            "🟡 Afinidad media"
                        )
                    elif row["Score"] >= 35:
                        st.info(
                            "🔵 Afinidad relevante"
                        )
                    else:
                        st.error(
                            "🔴 Afinidad baja"
                        )

                with bottom:
                    st.metric(
                        "Score",
                        f"{row['Score']}"
                    )

                st.progress(
                    min(
                        row["Score"] / 100,
                        1.0
                    )
                )

                with st.expander("🔬 Ver tema de investigación"):
                    st.write(row["Tema"])

                with st.expander("🎓 Ver formación académica"):
                    st.markdown(
                        f"""
                        **Nivel:** {row['Grado']}
                        
                        **Título:** {row['Formación']}
                        """
                    )

                with st.expander("📚 Ver publicaciones"):
                    publications = format_publications_for_display(row["Publicaciones"])

                    if publications:
                        st.markdown(
                            "\n".join(
                                f"- {publication}" for publication in publications
                            )
                        )
                    else:
                        st.info("No hay publicaciones registradas")

                st.divider()

else:

    st.info(
        "Escribe un tema para iniciar matching"
    )
