import streamlit as st

st.set_page_config(
    page_title="Sistema Editorial",
    layout="wide",
    initial_sidebar_state="expanded",
)

import pandas as pd
import plotly.express as px

from utils.reviewers import (
    load_reviewer_statuses,
    load_reviewers
)
from utils.auth import (
    login
)

if not login():

    st.stop()
# =========================
# CONFIG
# =========================

from utils.layout import (

    setup_page,

    render_sidebar
)
setup_page(
    "Dashboard"
)

render_sidebar()
# =========================
# DATA
# =========================

@st.cache_data(ttl=60)
def get_data():

    return load_reviewers()


@st.cache_data(ttl=60)
def get_status_data():

    return load_reviewer_statuses()


if st.button("Actualizar datos", key="refresh_dashboard"):

    get_data.clear()
    get_status_data.clear()

    st.rerun()


df = get_data()
status_by_reviewer = get_status_data()
# =========================
# TITLE
# =========================

st.title(
    "📊 Dashboard Editorial"
)

st.caption(
    "Sistema centralizado de gestión editorial"
)

st.divider()

# =========================
# MÉTRICAS
# =========================

m1, m2, m3, m4 = st.columns(4)

with m1:

    st.metric(
        "👨‍🏫 Evaluadores",
        len(df)
    )

with m2:

    st.metric(
        "🌎 Países",
        df["country"].nunique()
    )

with m3:

    st.metric(
        "🏛️ Instituciones",
        df["institution"].nunique()
    )

with m4:

    st.metric(
        "🎓 Grados",
        df["academic_degree_level"].nunique()
    )

st.divider()

# =========================
# ESTADO DE INVESTIGADORES
# =========================

status_counts = {
    "Activo": 0,
    "Inactivo": 0,
}

for status, _ in status_by_reviewer.values():
    if status == "🟢 Activo":
        status_counts["Activo"] += 1
    elif status in {"🔴 Inactivo", "⚪ Sin verificar", "🟡 Verificar"}:
        status_counts["Inactivo"] += 1

status_df = pd.DataFrame(
    {
        "Estado": ["Activo", "Inactivo"],
        "Investigadores": [
            status_counts["Activo"],
            status_counts["Inactivo"],
        ],
    }
)

st.subheader(
    "🧑‍🔬 Estado de investigadores"
)

status_cols = st.columns([1, 2])

with status_cols[0]:
    st.metric(
        "🟢 Activos",
        status_counts["Activo"]
    )
    st.metric(
        "🔴 Inactivos",
        status_counts["Inactivo"]
    )

with status_cols[1]:
    fig_status = px.pie(
        status_df,
        values="Investigadores",
        names="Estado",
        hole=0.45,
        color_discrete_map={
            "Activo": "#2ecc71",
            "Inactivo": "#e74c3c",
        },
    )
    fig_status.update_traces(textinfo="percent+value")

    st.plotly_chart(
        fig_status,
        use_container_width=True
    )

st.divider()

# =========================
# TOP PAÍSES
# =========================

top_countries = (

    df["country"]

    .value_counts()

    .head(10)

    .reset_index()
)

top_countries.columns = [

    "País",

    "Evaluadores"
]

fig = px.bar(

    top_countries,

    x="País",

    y="Evaluadores",

    text_auto=True
)

st.subheader(
    "🌎 Top países"
)

st.plotly_chart(

    fig,

    use_container_width=True
)

# =========================
# TOP INSTITUCIONES
# =========================

top_institutions = (

    df["institution"]

    .value_counts()

    .head(10)

    .reset_index()
)

top_institutions.columns = [

    "Institución",

    "Evaluadores"
]

fig2 = px.bar(

    top_institutions,

    x="Institución",

    y="Evaluadores",

    text_auto=True
)

st.subheader(
    "🏛️ Top instituciones"
)

st.plotly_chart(

    fig2,

    use_container_width=True
)

st.success(
    "🚀 Sistema funcionando correctamente"
)
