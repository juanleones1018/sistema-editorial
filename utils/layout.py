import streamlit as st

# =========================
# CONFIGURAR PÁGINA
# =========================

def setup_page(title):

    st.set_page_config(

        page_title=title,

        layout="wide",

        initial_sidebar_state="expanded"
    )

    # =========================
    # OCULTAR NAV STREAMLIT
    # =========================

    hide_streamlit_style = """

    <style>

    [data-testid="stSidebarNav"] {

        display: none;
    }

    </style>

    """

    st.markdown(

        hide_streamlit_style,

        unsafe_allow_html=True
    )

# =========================
# SIDEBAR
# =========================

def render_sidebar():

    with st.sidebar:

        st.title(
            "📚 Sistema Editorial"
        )

        st.caption(
            "Pares evaluadores"
        )

        st.divider()

        st.markdown(
            "## 🏠 Navegación"
        )

        # =========================
        # DASHBOARD
        # =========================

        if st.button(
            "🏠 Dashboard",
            use_container_width=True
        ):

            st.switch_page(
                "app.py"
            )

        # =========================
        # BUSCAR
        # =========================

        if st.button(
            "🔎 Buscar",
            use_container_width=True
        ):

            st.switch_page(
                "pages/1_Busqueda.py"
            )

        # =========================
        # MATCHING
        # =========================

        if st.button(
            "🎯 Matching",
            use_container_width=True
        ):

            st.switch_page(
                "pages/2_Matching.py"
            )

        # =========================
        # AGREGAR
        # =========================

        if st.button(
            "➕ Agregar",
            use_container_width=True
        ):

            st.switch_page(
                "pages/3_Agregar.py"
            )

        st.divider()

        st.success(
            "🚀 Sistema activo"
        )
        if st.button(
    "🚪 Cerrar sesión"
            ):
            
                st.session_state.clear()
            
                st.rerun()
