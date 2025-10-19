import streamlit as st
from services.supabase_client import (
    supabase, 
    get_current_user, 
    is_user_authenticated, 
    logout_user,
    get_user_email
)
import re

st.set_page_config(page_title="Login / Registro", layout="centered")

st.title("🔐 Login / Registro")

# Função para validar email
def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# Função para validar senha
def is_valid_password(password):
    return len(password) >= 6

# Verifica se o usuário já está logado
if is_user_authenticated():
    user_email = get_user_email()
    st.success(f"✅ Você já está logado como **{user_email}**!")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🚪 Logout", type="primary"):
            logout_user()
    
    with col2:
        if st.button("🏠 Ir para Página Inicial"):
            st.switch_page("0_Página_Inicial.py")
    
    st.markdown("---")
    st.info("💡 **Dica:** Use o menu lateral para navegar entre as páginas do aplicativo.")
    
else:
    st.info("🔑 Por favor, faça login ou registre-se para acessar o aplicativo.")

    tab1, tab2 = st.tabs(["🔑 Login", "📝 Registro"])

    with tab1:
        st.subheader("Entrar na sua conta")
        
        with st.form("login_form"):
            email_login = st.text_input(
                "📧 Email", 
                key="email_login",
                placeholder="seu.email@exemplo.com"
            )
            password_login = st.text_input(
                "🔒 Senha", 
                type="password", 
                key="password_login",
                placeholder="Digite sua senha"
            )
            
            col1, col2 = st.columns([1, 2])
            with col1:
                submitted_login = st.form_submit_button("🚀 Entrar", type="primary")

            if submitted_login:
                # Validações
                if not email_login or not password_login:
                    st.error("❌ Por favor, preencha todos os campos.")
                elif not is_valid_email(email_login):
                    st.error("❌ Por favor, insira um email válido.")
                else:
                    with st.spinner("🔄 Fazendo login..."):
                        try:
                            response = supabase.auth.sign_in_with_password({
                                "email": email_login, 
                                "password": password_login
                            })
                            
                            if response.user:
                                st.success("✅ Login realizado com sucesso!")
                                st.balloons()
                                st.rerun()
                            else:
                                st.error("❌ Email ou senha incorretos.")
                                
                        except Exception as e:
                            error_msg = str(e)
                            if "Invalid login credentials" in error_msg:
                                st.error("❌ Email ou senha incorretos.")
                            elif "Email not confirmed" in error_msg:
                                st.error("❌ Por favor, confirme seu email antes de fazer login.")
                            else:
                                st.error(f"❌ Erro inesperado: {error_msg}")

    with tab2:
        st.subheader("Criar nova conta")
        
        with st.form("register_form"):
            email_register = st.text_input(
                "📧 Email", 
                key="email_register",
                placeholder="seu.email@exemplo.com"
            )
            password_register = st.text_input(
                "🔒 Senha", 
                type="password", 
                key="password_register",
                placeholder="Mínimo 6 caracteres"
            )
            password_confirm = st.text_input(
                "🔒 Confirmar Senha", 
                type="password", 
                key="password_confirm",
                placeholder="Digite a senha novamente"
            )
            
            # Checkbox para aceitar termos (LGPD)
            accept_terms = st.checkbox(
                "📋 Aceito os termos de uso e política de privacidade (LGPD)",
                key="accept_terms"
            )
            
            col1, col2 = st.columns([1, 2])
            with col1:
                submitted_register = st.form_submit_button("📝 Registrar", type="primary")

            if submitted_register:
                # Validações
                if not email_register or not password_register or not password_confirm:
                    st.error("❌ Por favor, preencha todos os campos.")
                elif not is_valid_email(email_register):
                    st.error("❌ Por favor, insira um email válido.")
                elif not is_valid_password(password_register):
                    st.error("❌ A senha deve ter pelo menos 6 caracteres.")
                elif password_register != password_confirm:
                    st.error("❌ As senhas não coincidem.")
                elif not accept_terms:
                    st.error("❌ Você deve aceitar os termos de uso para se registrar.")
                else:
                    with st.spinner("🔄 Criando conta..."):
                        try:
                            response = supabase.auth.sign_up({
                                "email": email_register, 
                                "password": password_register
                            })
                            
                            if response.user:
                                st.success("✅ Registro realizado com sucesso!")
                                st.info("📧 Verifique seu email para confirmar sua conta antes de fazer login.")
                                st.balloons()
                            else:
                                st.error("❌ Erro ao criar conta. Tente novamente.")
                                
                        except Exception as e:
                            error_msg = str(e)
                            if "User already registered" in error_msg:
                                st.error("❌ Este email já está registrado. Tente fazer login.")
                            else:
                                st.error(f"❌ Erro inesperado: {error_msg}")

# Informações sobre LGPD
with st.expander("📋 Informações sobre Privacidade (LGPD)"):
    st.markdown("""
    **🔒 Proteção de Dados Pessoais**
    
    Em conformidade com a Lei Geral de Proteção de Dados (LGPD), informamos que:
    
    - ✅ Suas informações de compras são privadas e visíveis apenas para você
    - ✅ Não compartilhamos seus dados com terceiros
    - ✅ Você pode solicitar a exclusão de seus dados a qualquer momento
    - ✅ Os dados de registro de mercados são compartilhados para benefício da comunidade
        **📧 Contato:** Para questões sobre privacidade, entre em contato conosco: gh.sabino@gmail.com
    """)

# Rodapé
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>"
    "🛡️ Seus dados estão protegidos conforme a LGPD"
    "</div>", 
    unsafe_allow_html=True
)


