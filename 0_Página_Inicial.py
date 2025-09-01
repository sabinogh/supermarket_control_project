import streamlit as st

st.set_page_config(page_title="Página Inicial", layout="wide")

st.sidebar.title("Menu de Navegação")
st.sidebar.markdown("""GSproject""")

st.title("📊 Controle de Gastos no Mercado")
st.write("Bem-vindo ao seu painel de controle!")

st.markdown("""
### O que você pode fazer:
- 📝 **Registrar Compras** (notas, itens, valores)
- 📈 **Analisar Compras** (gráficos, estatísticas e tendências)
- 🏪 **Cadastrar Mercados**
""")

st.info("Use o menu lateral para navegar entre as páginas.")