
import streamlit as st
from supabase import create_client
import os
from typing import Optional, Dict, Any
from dotenv import load_dotenv
load_dotenv()

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

# Funções de autenticação
def get_current_user():
    """Retorna o usuário atual autenticado"""
    try:
        response = supabase.auth.get_user()
        return response.user if response else None
    except Exception as e:
        st.error(f"Erro ao obter usuário: {e}")
        return None

def is_user_authenticated() -> bool:
    """Verifica se o usuário está autenticado"""
    user = get_current_user()
    return user is not None

def require_authentication():
    """Força autenticação - redireciona para login se não autenticado"""
    if not is_user_authenticated():
        st.warning("🔒 Você precisa fazer login para acessar esta página.")
        st.info("👈 Use o menu lateral para ir para a página de Login.")
        st.stop()

def get_user_id() -> Optional[str]:
    """Retorna o ID do usuário atual"""
    user = get_current_user()
    return user.id if user else None

def get_user_email() -> Optional[str]:
    """Retorna o email do usuário atual"""
    user = get_current_user()
    return user.email if user else None

def is_admin_user() -> bool:
    """Verifica se o usuário atual é administrador"""
    user_email = get_user_email()
    # Lista de emails de administradores (pode ser configurada via variável de ambiente)
    admin_emails = os.getenv("ADMIN_EMAILS", "").split(",")
    return user_email in admin_emails if user_email else False

def logout_user():
    """Faz logout do usuário atual"""
    try:
        supabase.auth.sign_out()
        # Limpa dados da sessão
        for key in list(st.session_state.keys()):
            if key.startswith('user_'):
                del st.session_state[key]
        st.success("Logout realizado com sucesso!")
        st.rerun()
    except Exception as e:
        st.error(f"Erro ao fazer logout: {e}")

# Funções de gerenciamento de dados com isolamento por usuário
def get_user_data(table_name: str, filters: Dict[str, Any] = None) -> list:
    """Busca dados específicos do usuário atual"""
    user_id = get_user_id()
    if not user_id:
        return []
    
    query = supabase.table(table_name).select("*").eq("user_id", user_id)
    
    if filters:
        for key, value in filters.items():
            query = query.eq(key, value)
    
    try:
        response = query.execute()
        return response.data if response.data else []
    except Exception as e:
        st.error(f"Erro ao buscar dados: {e}")
        return []

def insert_user_data(table_name: str, data: Dict[str, Any]) -> bool:
    """Insere dados associados ao usuário atual"""
    user_id = get_user_id()
    if not user_id:
        st.error("Usuário não autenticado")
        return False
    
    # Adiciona o user_id aos dados
    data["user_id"] = user_id
    
    try:
        response = supabase.table(table_name).insert(data).execute()
        return True
    except Exception as e:
        st.error(f"Erro ao inserir dados: {e}")
        return False


