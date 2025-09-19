import streamlit as st
from services import db_queries
from services.supabase_client import (
    require_authentication, 
    get_user_email, 
    get_user_id,
    supabase
)
import pandas as pd

st.set_page_config(page_title="Gerenciar Mercados", layout="wide")

# Força autenticação
require_authentication()

# Configuração da sidebar
st.sidebar.title("🛒 Menu de Navegação")
st.sidebar.markdown("**GSproject**")
st.sidebar.markdown("---")
st.sidebar.markdown(f"👤 **{get_user_email()}**")

st.title("🏪 Gerenciar Mercados")
st.write("Visualize todos os mercados da comunidade e adicione novos estabelecimentos.")

# Informação sobre funcionalidade comunitária
st.info("🤝 **Funcionalidade Comunitária:** Os mercados são compartilhados entre todos os usuários para benefício da comunidade.")

# Tabs para diferentes funcionalidades
tab1, tab2 = st.tabs(["🏬 Ver Mercados", "➕ Adicionar Mercado"])

with tab1:
    st.subheader("🏬 Mercados Disponíveis")
    
    # Buscar todos os mercados
    try:
        mercados = db_queries.buscar_mercados()
        
        if mercados:
            df_mercados = pd.DataFrame(mercados)
            
            # Buscar informações de quem adicionou cada mercado (se disponível)
            try:
                # Query para buscar mercados com informação do usuário que adicionou
                response = supabase.table("mercados").select("""
                    id,
                    nome,
                    cidade,
                    created_at
                """).execute()
                
                if response.data:
                    df_mercados_completo = pd.DataFrame(response.data)
                    # Formatar data
                    df_mercados_completo['created_at'] = pd.to_datetime(df_mercados_completo['created_at']).dt.strftime('%Y/%m/%d')
                    # Renomear colunas para exibição
                    df_display = df_mercados_completo.rename(columns={
                        "nome": "Nome",
                        "cidade": "Cidade",
                        "created_at": "Adicionado em"
                    })
                    # Remover colunas técnicas
                    df_display = df_display.drop(columns=["id", "added_by_user_id"], errors="ignore")
                    st.success(f"✅ Encontrados {len(df_display)} mercados cadastrados na comunidade!")
                    # Filtros
                    cidades_disponiveis = ["Todas"] + sorted(df_display["Cidade"].unique().tolist())
                    cidade_filtro = st.selectbox("🏙️ Filtrar por Cidade", cidades_disponiveis)
                    # Aplicar filtro
                    df_filtrado = df_display.copy()
                    if cidade_filtro != "Todas":
                        df_filtrado = df_filtrado[df_filtrado["Cidade"] == cidade_filtro]
                    if not df_filtrado.empty:
                        st.dataframe(df_filtrado, use_container_width=True)
                        # Estatísticas
                        st.markdown("---")
                        st.metric("🏪 Total de Mercados", len(df_filtrado))
                    else:
                        st.info("📭 Nenhum mercado encontrado com os filtros selecionados.")
                
                else:
                    # Fallback para dados básicos
                    df_display = df_mercados.rename(columns={
                        "nome": "Nome",
                        "cidade": "Cidade"
                    })
                    st.dataframe(df_display, use_container_width=True)
                    
            except Exception as e:
                st.warning(f"⚠️ Erro ao buscar detalhes dos mercados: {e}")
                # Exibir dados básicos
                df_display = df_mercados.rename(columns={
                    "nome": "Nome",
                    "cidade": "Cidade"
                })
                st.dataframe(df_display, use_container_width=True)
        else:
            st.info("📭 Nenhum mercado cadastrado ainda. Seja o primeiro a adicionar um mercado!")
            
    except Exception as e:
        st.error(f"❌ Erro ao buscar mercados: {e}")

with tab2:
    st.subheader("➕ Adicionar Novo Mercado")
    st.write("Contribua com a comunidade adicionando um novo mercado!")
    
    with st.form("add_mercado_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            nome = st.text_input("🏪 Nome do Mercado *", placeholder="Ex: Supermercado ABC")
            cidade = st.text_input("🏙️ Cidade *", placeholder="Ex: São Paulo")
        
        with col2:
            # Estado removido pois não existe na tabela
            telefone = st.text_input("📞 Telefone", placeholder="Ex: (11) 1234-5678")
        
        st.markdown("**Campos marcados com * são obrigatórios*")
        
        submitted = st.form_submit_button("🚀 Adicionar Mercado", type="primary")
        
        if submitted:
            # Validações
            if not nome or not cidade:
                st.error("❌ Por favor, preencha todos os campos obrigatórios.")
            elif len(nome) < 3:
                st.error("❌ O nome do mercado deve ter pelo menos 3 caracteres.")
            elif len(cidade) < 2:
                st.error("❌ O nome da cidade deve ter pelo menos 2 caracteres.")
            else:
                try:
                    user_id = get_user_id()
                    # Dados do mercado
                    mercado_data = {
                        "nome": nome.strip(),
                        "cidade": cidade.strip(),
                        "telefone": telefone.strip() if telefone else None,
                        "added_by_user_id": user_id
                    }
                    
                    # Verificar se mercado já existe
                    existing = supabase.table("mercados").select("id").eq("nome", nome.strip()).eq("cidade", cidade.strip()).execute()
                    
                    if existing.data:
                        st.warning("⚠️ Já existe um mercado com este nome nesta cidade.")
                    else:
                        # Inserir mercado
                        response = supabase.table("mercados").insert(mercado_data).execute()
                        
                        if response.data:
                            st.success("✅ Mercado adicionado com sucesso!")
                            st.balloons()
                            st.info("🔄 Recarregue a página para ver o mercado na lista.")
                        else:
                            st.error("❌ Erro ao adicionar mercado. Tente novamente.")
                            
                except Exception as e:
                    st.error(f"❌ Erro ao adicionar mercado: {e}")

# Informações sobre contribuição comunitária
st.markdown("---")
with st.expander("ℹ️ Sobre a Funcionalidade Comunitária"):
    st.markdown("""
    **🤝 Como funciona a funcionalidade comunitária de mercados:**
    
    - ✅ **Compartilhamento:** Todos os mercados são visíveis para todos os usuários
    - ✅ **Contribuição:** Qualquer usuário pode adicionar novos mercados
    - ✅ **Benefício Mútuo:** Quanto mais mercados cadastrados, melhor para toda a comunidade
    - ✅ **Rastreabilidade:** O sistema registra quem adicionou cada mercado
    - ✅ **Privacidade:** Apenas os mercados são compartilhados, suas compras permanecem privadas
    
    **📝 Dicas para adicionar mercados:**
    - Verifique se o mercado já não está cadastrado
    - Use nomes completos e oficiais dos estabelecimentos
    - Inclua endereços completos para facilitar a localização
    - Adicione telefone quando disponível para contato
    """)

# Rodapé
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666; font-size: 0.9em;'>"
    "🤝 Mercados compartilhados pela comunidade | 🔒 Suas compras permanecem privadas"
    "</div>", 
    unsafe_allow_html=True
)
