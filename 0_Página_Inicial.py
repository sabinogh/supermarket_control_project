import streamlit as st
from services.supabase_client import supabase

st.set_page_config(page_title="Página Inicial", layout="wide")

st.sidebar.title("Menu de Navegação")
st.sidebar.markdown("GSproject")

# Verifica o estado de autenticação
user = supabase.auth.get_user()

if not user:
    st.warning("Você precisa fazer login para acessar o aplicativo.")
    st.stop() # Para a execução do script se não estiver logado

st.title("📊 Controle de Gastos - Mercado")
st.write(f"Bem-vindo, {user.user.email}! Este é o seu painel de controle.")

st.markdown("""
### O que você pode fazer:
- 📝 **Registrar Compras** (notas, itens, valores)
- 📈 **Analisar Compras** (gráficos, estatísticas e tendências)
- 🏪 **Cadastrar Mercados**
""")

st.info("Use o menu lateral para navegar entre as páginas.")

# Botão de Logout na sidebar
if st.sidebar.button("Logout"):
    supabase.auth.sign_out()
    st.session_state.user = None # Limpa o estado da sessão
    st.success("Logout realizado com sucesso!")
    st.rerun() # Força um rerun para atualizar o estado da página
