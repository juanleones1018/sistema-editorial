import streamlit as st


def login():

    if st.session_state.get(
        "authenticated",
        False
    ):
        return True

    st.title(
        "🔐 Sistema Editorial"
    )

    username = st.text_input(
        "Usuario"
    )

    password = st.text_input(
        "Contraseña",
        type="password"
    )

    if st.button(
        "Ingresar"
    ):

        if (

            username
            ==
            st.secrets["APP_USER"]

            and

            password
            ==
            st.secrets["APP_PASSWORD"]

        ):

            st.session_state[
                "authenticated"
            ] = True

            st.rerun()

        else:

            st.error(
                "Credenciales incorrectas"
            )

    return False
