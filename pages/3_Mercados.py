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

require_authentication()

# Definir tabs corretamente
tab1, tab2 = st.tabs(["Ver Mercados", "Adicionar Mercado"])

with tab1:
    st.subheader("🏪 Mercados Cadastrados")
    st.write("Veja todos os mercados disponíveis para registrar suas compras.")
    try:
        mercados = supabase.table("mercados").select("*").order("nome", desc=False).execute().data
        if mercados:
            df_mercados = pd.DataFrame(mercados)
            # Exibe os campos concatenados
            df_mercados["Mercado"] = (
                df_mercados["nome"] + ", " +
                df_mercados["cidade"] + ", " +
                df_mercados["estado"] + ", " +
                df_mercados["rua"] + ", " +
                df_mercados["numero"] + ", " +
                df_mercados["cep"]
            )
            st.dataframe(df_mercados[["Mercado", "cnpj"]], use_container_width=True)
        else:
            st.info("Nenhum mercado cadastrado ainda.")
    except Exception as e:
        st.error(f"Erro ao buscar mercados: {e}")

with tab2:
    st.subheader("➕ Adicionar Novo Mercado")
    st.write("Contribua com a comunidade adicionando um novo mercado!")
    with st.form("add_mercado_form"):
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("🏪 Nome do Mercado *", placeholder="Ex: Supermercado ABC", key="nome_mercado_form")
            cidade = st.text_input("🏙️ Cidade *", placeholder="Ex: São Paulo", key="cidade_mercado_form")
        with col2:
            cnpj = st.text_input("🔢 CNPJ *", placeholder="Ex: 12.345.678/0001-99", key="cnpj_mercado_form")
            rua = st.text_input("🏠 Rua *", placeholder="Ex: Av. Brasil", key="rua_mercado_form")
            numero = st.text_input("# Número *", placeholder="Ex: 123", key="numero_mercado_form")
            cep = st.text_input("📮 CEP *", placeholder="Ex: 12345-678", key="cep_mercado_form")
            estados_brasil = [
                "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"
            ]
            estado = st.selectbox("🌎 Estado *", estados_brasil, key="estado_mercado_form")
        st.markdown("**Todos os campos são obrigatórios*")
        submitted = st.form_submit_button("🚀 Adicionar Mercado", type="primary")
        if submitted:
            # Validações
            if not (nome and cidade and cnpj and rua and numero and cep and estado):
                st.error("❌ Por favor, preencha todos os campos obrigatórios.")
            elif len(nome) < 3:
                st.error("❌ O nome do mercado deve ter pelo menos 3 caracteres.")
            elif len(cidade) < 2:
                st.error("❌ O nome da cidade deve ter pelo menos 2 caracteres.")
            elif len(cnpj) < 14:
                st.error("❌ O CNPJ deve ter pelo menos 14 dígitos.")
            elif len(cep) < 8:
                st.error("❌ O CEP deve ter pelo menos 8 dígitos.")
            else:
                try:
                    user_id = get_user_id()
                    mercado_data = {
                        "nome": nome.strip(),
                        "cidade": cidade.strip(),
                        "cnpj": cnpj.strip(),
                        "rua": rua.strip(),
                        "numero": numero.strip(),
                        "cep": cep.strip(),
                        "estado": estado,
                        "added_by_user_id": user_id
                    }
                    existing = supabase.table("mercados").select("id").eq("nome", nome.strip()).eq("cidade", cidade.strip()).execute()
                    if existing.data:
                        st.warning("⚠️ Já existe um mercado com este nome nesta cidade.")
                    else:
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
    **🤝 Funcionalidade Comunitária de Mercados**

    - ✅ **Compartilhamento público de mercados:** mercados cadastrados são visíveis para todos os usuários
    - ✅ **Contribuição aberta:** qualquer usuário pode adicionar mercados para ampliar a base
    - ✅ **Privacidade preservada:** somente os cadastros de mercados são públicos; suas compras continuam privadas

    **📝 Boas práticas ao adicionar um mercado:**
    - Verifique se já não existe o mesmo mercado cadastrado
    - Utilize o nome oficial e um endereço completo
    """)

# Rodapé
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666; font-size: 0.9em;'>"
    "🤝 Mercados compartilhados pela comunidade | 🔒 Suas compras permanecem privadas"
    "</div>", 
    unsafe_allow_html=True
)
