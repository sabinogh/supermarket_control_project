import streamlit as st
import pandas as pd
from services import db_queries
import datetime

st.title("📊 Análise de Compras")

st.write("Selecione o período para analisar suas compras:")

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
            # Busca dados para estatísticas (cabeçalho)
            compras_cabecalho = db_queries.get_compras_cabecalho_periodo(data_inicio, data_fim)
            # Chama a função RPC para obter os dados detalhados para a tabela
            compras_detalhadas = db_queries.get_compras_detalhadas_rpc(data_inicio, data_fim)

            if compras_cabecalho and compras_detalhadas:
                df_cabecalho = pd.DataFrame(compras_cabecalho)
                df_detalhadas = pd.DataFrame(compras_detalhadas)

                if not df_cabecalho.empty and not df_detalhadas.empty:
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
                        
                        # Para filtrar o cabeçalho, precisamos dos IDs dos mercados correspondentes aos nomes selecionados
                        # e das datas de compra presentes nos itens detalhados filtrados.
                        
                        # Obter os IDs dos mercados selecionados a partir dos nomes
                        todos_mercados_db = db_queries.buscar_mercados()
                        df_todos_mercados = pd.DataFrame(todos_mercados_db)
                        
                        # Filtrar os IDs dos mercados com base nos nomes selecionados
                        mercado_ids_selecionados = df_todos_mercados[
                            df_todos_mercados["nome"].isin(mercados_selecionados)
                        ]["id"].tolist()

                        # Filtrar o DataFrame de cabeçalho com base nos IDs dos mercados selecionados
                        df_cabecalho_filtrado = df_cabecalho[
                            df_cabecalho["mercado_id"].isin(mercado_ids_selecionados)
                        ]

                        if not df_detalhadas_filtrado.empty:
                            # ======================
                            # Estatísticas
                            # ======================
                            st.subheader("📈 Estatísticas do Período")
                            col1, col2, col3 = st.columns(3)

                            # Total Gasto: Somatória dos valores do DB "compras_item[valor_total]"
                            total_gasto = df_detalhadas_filtrado["valor_total"].sum()
                            with col1:
                                st.metric("Total Gasto", f"R$ {total_gasto:.2f}")

                            # Total Desconto: Somatória dos valores do DB "compras_cabecalho[descontos]"
                            total_desconto = df_cabecalho_filtrado["descontos"].sum()
                            with col2:
                                st.metric("Total Desconto", f"R$ {total_desconto:.2f}")

                            # Valor Final Pago: Resultado de "compras_item[valor_total]" - "compras_cabecalho[descontos]"
                            valor_final_pago = total_gasto - total_desconto
                            with col3:
                                st.metric("Valor Final Pago", f"R$ {valor_final_pago:.2f}")

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


