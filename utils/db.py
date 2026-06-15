import streamlit as st


print("Cargando db.py...")
print("Secrets disponibles:")

try:
    print(st.secrets.keys())
except Exception as e:
    print(e)
    raise
from supabase import (
    create_client
)

SUPABASE_URL = (
    st.secrets[
        "SUPABASE_URL"
    ]
)

SUPABASE_KEY = (
    st.secrets[
        "SUPABASE_KEY"
    ]
)

supabase = create_client(

    SUPABASE_URL,

    SUPABASE_KEY
)
