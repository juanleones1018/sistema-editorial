import streamlit as st
import pandas as pd
from utils.auth import (
    login
)

if not login():
    st.stop()
from utils.matching import (
    calculate_match_score
)
from utils.reviewers import (

    load_reviewers,

    load_reviewer_statuses,
    set_reviewer_status
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
    page_title="Matching",
    layout="wide"
)

# =========================
# LOAD DATA
# =========================

@st.cache_data
def get_data():

    return load_reviewers()

df = get_data()
status_dict = load_reviewer_statuses()
# =========================
# VALIDAR
# =========================

if df.empty:

    st.warning(
        "No hay evaluadores"
    )

    st.stop()

# =========================
# LIMPIAR
# =========================

df = df.fillna("")

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

    title = st.text_input(
        "Título artículo"
    )

    query = st.text_area(

        "Resumen / descripción",

        height=220,

        placeholder="""
Describe el artículo, tema o enfoque de investigación...
"""
    )

    keywords = st.text_input(
        "Palabras clave separadas por coma"
    )

# =========================
# PANEL DERECHO
# =========================

with right:

    st.subheader(
        "⚙️ Configuración"
    )

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

    active_ids = [

        reviewer_id

        for reviewer_id, (
            status,
            _
        ) in status_dict.items()

        if status == "🟢 Activo"
    ]

    filtered_df = filtered_df[

        filtered_df["id"].isin(
            active_ids
        )
    ]

# =========================
# QUERY FINAL
# =========================

full_query = (

    str(title)

    +

    " "

    +

    str(query)

    +

    " "

    +

    str(keywords)
)

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

        final_score = calculate_match_score(

            row,

            full_query,

            thematic_weight,

            publication_weight
        )

        status, source = status_dict.get(

            row["id"],
        
            (
                "🟡 Sin verificar",
                None
            )
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
                    new_status = st.selectbox(

                            "Actualizar estado",
                        
                            [
                        
                                "Sin cambios",
                        
                                "🟢 Activo",
                        
                                "🟡 Revisión editorial",
                        
                                "🔴 No disponible"
                        
                            ],
                        
                            key=f"status_{row['ID']}"
                        )
                    if st.button(

                            "Guardar",
                        
                            key=f"save_{row['ID']}"
                        ):
                        
                            if new_status != "Sin cambios":
                        
                                set_reviewer_status(
                        
                                    reviewer_id=row["ID"],
                        
                                    is_active=(
                                        new_status == "🟢 Activo"
                                    ),
                        
                                    source="Editorial",
                        
                                    notes=f"Actualizado desde Matching: {new_status}"
                                )
                        
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

                        if row["Score"] >= 80:

                            st.success(
                                "Alta afinidad"
                            )

                        elif row["Score"] >= 60:

                            st.warning(
                                "Afinidad media"
                            )

                        else:

                            st.error(
                                "Afinidad baja"
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

                with st.expander(

                    "🔬 Ver tema de investigación"
                ):

                    st.write(
                        row["Tema"]
                    )
                with st.expander(
                    "🎓 Ver formación académica"
                 ):
                    
                    st.markdown(
                            f"""
                            **Nivel:** {row['Grado']}
                            
                            **Título:** {row['Formación']}
                            """
                    )
                with st.expander(
                        "📚 Ver publicaciones"
                 ):
                        st.write(
                           row["Publicaciones"]
                    )
                st.divider()

else:

    st.info(
        "Escribe un tema para iniciar matching"
    )
   
