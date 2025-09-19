import streamlit as st
from supabase import create_client
import os

@st.cache_resource
def init_supabase_client():
    try:
        # Se existir no Streamlit Cloud, usa secrets
        supabase_url = st.secrets["SUPABASE_URL"]
        supabase_key = st.secrets["SUPABASE_KEY"]
    except Exception:
        # Caso contrário, pega das variáveis de ambiente (localhost)
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        st.error("Credenciais do Supabase não configuradas. Verifique st.secrets ou variáveis de ambiente.")
        st.stop()

    return create_client(supabase_url, supabase_key)

supabase = init_supabase_client()
