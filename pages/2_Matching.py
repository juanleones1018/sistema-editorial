import streamlit as st
import pandas as pd

from rapidfuzz import fuzz

from utils.reviewers import (
    load_reviewers
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
        "### 📊 Criterios"
    )

    thematic_weight = st.slider(

        "Afinidad temática",

        0,

        100,

        70
    )

    publication_weight = st.slider(

        "Publicaciones",

        0,

        100,

        30
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

if full_query.strip():

    scores = []

    for _, row in filtered_df.iterrows():

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

        # =========================
        # SCORE TEMÁTICO
        # =========================

        topic_score = fuzz.token_set_ratio(

            full_query,

            topic
        )

        # =========================
        # SCORE PUBLICACIONES
        # =========================

        publication_score = (
            fuzz.token_set_ratio(

                full_query,

                publications
            )
        )

        # =========================
        # SCORE FINAL
        # =========================

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

        # =========================
        # BONUS PUBLICACIÓN RECIENTE
        # =========================

        try:

            last_year = int(

                row.get(
                    "last_publication_year",
                    0
                )
            )

            if last_year >= 2022:

                final_score += 5

        except:

            pass

        scores.append({

            "Nombre":
                row["full_name"],
        
            "Correo":
                row["email"],
        
            "Institución":
                row["institution"],
        
            "País":
                row["country"],
        
            "Nivel":
                row["academic_degree_level"],
        
            "Última publicación":
                row["last_publication_year"],
        
            "Score":
                round(final_score, 1),
        
            "Tema":
                topic[:300]
        })

    # =========================
    # RESULTADOS
    # =========================

    results_df = pd.DataFrame(
        scores
    )

    results_df = results_df.sort_values(

        by="Score",

        ascending=False
    )

    results_df = results_df.head(30)

    st.subheader(
        "🏆 Mejores coincidencias"
    )

   # =========================
# CARDS
# =========================

    for idx, row in results_df.iterrows():
    
        with st.container():
    
            top, bottom = st.columns([5, 1])
    
            # =========================
            # IZQUIERDA
            # =========================
    
            with top:
    
                st.markdown(
                    f"### 👨‍🏫 {row['Nombre']}"
                )
    
                st.caption(
                    f"🏛 {row['Institución']} • 🌎 {row['País']}"
                )
    
                # =========================
                # CORREO
                # =========================
    
                st.text_input(
    
                    "📧 Correo de contacto",
    
                    value=row["Correo"],
    
                   
    
                    key=f"email_{idx}"
                )
    
                badge1, badge2, badge3 = st.columns(3)
    
                with badge1:
    
                    st.success(
                        row["Nivel"]
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
    
            # =========================
            # DERECHA
            # =========================
    
            with bottom:
    
                st.metric(
                    "Score",
                    f"{row['Score']}"
                )
    
            # =========================
            # BARRA SCORE
            # =========================
    
            st.progress(
                min(
                    row["Score"] / 100,
                    1.0
                )
            )
    
            # =========================
            # TEMA
            # =========================
    
            with st.expander(
                "🔬 Ver tema de investigación"
            ):
    
                st.write(
                    row["Tema"]
                )
    
            st.divider()
    
    else:
    
        st.info(
            "Escribe un tema para iniciar matching"
        )
   
