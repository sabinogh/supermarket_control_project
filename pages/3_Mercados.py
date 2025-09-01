import streamlit as st
from services import db_queries
import pandas as pd

st.sidebar.title("Menu de Navegação")
st.sidebar.markdown("""GSproject""")

st.title("🏪 Cadastro e Consulta de Mercados")

st.header("Cadastrar novo mercado")
with st.form("form_cadastro_mercado"):
    nome_mercado = st.text_input("Nome do Mercado")
    cidade_mercado = st.text_input("Cidade")
    submitted = st.form_submit_button("Registrar Mercado")
    if submitted:
        if nome_mercado and cidade_mercado:
            mercado = db_queries.registrar_mercado(nome_mercado, cidade_mercado)
            if mercado:
                st.success(f"Mercado '{nome_mercado}' cadastrado!")
                st.rerun()
        else:
            st.warning("Preencha todos os campos para cadastrar o mercado.")

st.header("Mercados cadastrados")
mercados = db_queries.buscar_mercados()
if mercados:
    df = pd.DataFrame(mercados)
    if 'created_at' in df.columns:
        df = df.rename(columns={'created_at': 'Data Registro'})
        df['Data Registro'] = pd.to_datetime(df['Data Registro']).dt.strftime('%d/%m/%Y')
    st.dataframe(df)
else:
    st.info("Nenhum mercado cadastrado ainda.")
