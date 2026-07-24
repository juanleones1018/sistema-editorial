import streamlit as st

st.set_page_config(
    page_title="Sistema Editorial",
    layout="wide",
    initial_sidebar_state="expanded",
)

import pandas as pd
import plotly.express as px

from utils.reviewers import (
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

if st.button("Actualizar datos", key="refresh_dashboard"):

    get_data.clear()

    st.rerun()

df = get_data()

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
