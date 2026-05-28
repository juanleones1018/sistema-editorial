import streamlit as st
import pandas as pd
import plotly.express as px

from utils.reviewers import (
    load_reviewers
)

from utils.layout import (

    setup_page,

    render_sidebar
)

# =========================
# CONFIG
# =========================

setup_page(
    "Dashboard"
)

render_sidebar()