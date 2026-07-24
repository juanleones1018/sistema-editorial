import os

import streamlit as st
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = (
    st.secrets.get("SUPABASE_URL")
    or os.environ.get("SUPABASE_URL")
)

SUPABASE_KEY = (
    st.secrets.get("SUPABASE_KEY")
    or os.environ.get("SUPABASE_KEY")
)

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError(
        "SUPABASE_URL and SUPABASE_KEY are required. "
        "Set them in .streamlit/secrets.toml or in environment variables."
    )


def get_supabase():
    return create_client(
        SUPABASE_URL,
        SUPABASE_KEY,
    )

supabase = get_supabase()
