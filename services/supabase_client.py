import streamlit as st
from supabase import create_client

SUPABASE_URL = st.secrets["https://wufmrqnmzcykiytqynhv.supabase.co"]
SUPABASE_KEY = st.secrets["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind1Zm1ycW5temN5a2l5dHF5bmh2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTUyNTk2NzUsImV4cCI6MjA3MDgzNTY3NX0.lx44jf873UGPZZnCruSbEMLnnn8ya8N3dsXji_8w3YA"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
