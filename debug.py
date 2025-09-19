import streamlit as st
from supabase import create_client

def main():
    st.title("🔍 Teste de Conexão com Supabase")

    try:
        SUPABASE_URL = st.secrets["SUPABASE_URL"]
        SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

        st.write("✅ Secrets carregados com sucesso")

        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

        # Testa conexão pegando as tabelas do banco
        response = supabase.table("compras_itens").select("*").limit(1).execute()

        st.write("✅ Conexão bem-sucedida!")
        st.json(response.data)

    except Exception as e:
        st.error("❌ Erro ao conectar no Supabase")
        st.exception(e)

if __name__ == "__main__":
    main()
