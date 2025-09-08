import streamlit as st
import pandas as pd
from services import db_queries
import datetime

st.sidebar.title("Menu de Navegação")
st.sidebar.markdown("""GSproject""")

st.title("📊 Análise de Compras")

st.write("Selecione o período para visualizar as compras básicas.")

# Seleção de período
col1, col2 = st.columns(2)

with col1:
    data_inicio = st.date_input(
        "Data de Início",
        value=datetime.date.today() - datetime.timedelta(days=30),
        max_value=datetime.date.today()
    )

with col2:
    data_fim = st.date_input(
        "Data de Fim",
        value=datetime.date.today(),
        max_value=datetime.date.today()
    )

# Botão para buscar
if st.button("🔍 Buscar Compras"):
    if data_inicio > data_fim:
        st.error("❌ A data de início deve ser menor ou igual à data de fim.")
    else:
        with st.spinner("Buscando compras..."):
            # Chama a função RPC para obter os dados detalhados para a tabela
            compras_detalhadas = db_queries.get_compras_detalhadas_rpc(data_inicio, data_fim)

            if compras_detalhadas:
                df_detalhadas = pd.DataFrame(compras_detalhadas)

                if not df_detalhadas.empty:
                    st.success(f"✅ Encontrados {len(df_detalhadas)} itens de compras no período selecionado!")

                    # ======================
                    # Filtro de Mercado
                    # ======================
                    mercados_disponiveis = df_detalhadas["mercado"].unique().tolist()
                    mercados_selecionados = st.multiselect(
                        "Filtrar por Mercado",
                        options=mercados_disponiveis,
                        default=mercados_disponiveis # Seleciona todos por padrão
                    )

                    if mercados_selecionados:
                        df_detalhadas_filtrado = df_detalhadas[df_detalhadas["mercado"].isin(mercados_selecionados)]
                        
                        if not df_detalhadas_filtrado.empty:
                            # ======================
                            # Tabela de Compras
                            # ======================
                            st.subheader("📋 Compras do Período")

                            df_visualizacao = df_detalhadas_filtrado.drop(columns=["desconto"], errors="ignore").rename(columns={
                                "data_compra": "Data da Compra",
                                "item": "Item",
                                "descricao": "Descrição",
                                "quantidade": "Quantidade",
                                "unidade": "Unidade",
                                "valor_unitario": "Valor Unitário",
                                "valor_total": "Valor Total",
                                "mercado": "Mercado",
                                "cidade": "Cidade"
                            })

                            st.dataframe(df_visualizacao, use_container_width=True)

                            # ======================
                            # Download dos Dados
                            # ======================
                            csv = df_visualizacao.to_csv(index=False, sep=";")
                            st.download_button(
                                label="📥 Download CSV",
                                data=csv,
                                file_name=f"compras_detalhadas_{data_inicio}_{data_fim}.csv",
                                mime="text/csv"
                            )

                        else:
                            st.info("📭 Nenhuma compra encontrada para os mercados selecionados no período.")
                    else:
                        st.info("Por favor, selecione ao menos um mercado para filtrar.")

                else:
                    st.info("📭 Nenhuma compra encontrada no período selecionado.")
            else:
                st.error("❌ Erro ao buscar compras. Verifique a conexão com o banco de dados ou se há dados no período.")
