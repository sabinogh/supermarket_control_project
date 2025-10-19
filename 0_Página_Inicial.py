import streamlit as st
from services.supabase_client import (
    require_authentication,
    get_user_email,
    supabase
)

st.set_page_config(page_title="Página Inicial", layout="wide")

require_authentication()

st.sidebar.title("Menu de Navegação")
user_email = get_user_email()
if user_email:
    st.sidebar.markdown(f"👤 **{user_email}**")

# Pequena identificação no sidebar (texto simples)
st.sidebar.markdown("GSproject")

st.title("Página Inicial")
if user_email:
    st.write(f"Bem-vindo, {user_email}! Este é o seu painel de controle.")
else:
    st.write("Bem-vindo! Faça login para acessar todas as funcionalidades.")

st.markdown("""
### O que você pode fazer:
- 📝 **Registrar Compras** (notas, itens, valores)
- 📈 **Analisar Compras** (gráficos, estatísticas e tendências)
- 🏪 **Cadastrar Mercados**
""")

st.info("Use o menu lateral para navegar entre as páginas.")

# Botão de Logout na sidebar
if st.sidebar.button("Logout"):
    try:
        supabase.auth.sign_out()
    except Exception:
        pass
    st.session_state.pop("user", None)
    st.success("Logout realizado com sucesso!")
    st.experimental_rerun()
