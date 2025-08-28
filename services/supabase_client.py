from supabase import create_client
from dotenv import load_dotenv
import os
import streamlit as st

# Carrega variáveis do .env quando rodando no localhost
load_dotenv()

try:
    # Se existir no Streamlit Cloud, usa secrets
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
except Exception:
    # Caso contrário, pega do .env (localhost)
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
