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
                    # Estatísticas
                    # ======================
                    st.subheader("📈 Estatísticas do Período")
                    col1, col2, col3 = st.columns(3)

                    # Total Gasto: Somatória dos valores do DB "compras_item[valor_total]"
                    total_gasto = df_detalhadas["valor_total"].sum()
                    with col1:
                        st.metric("Total Gasto", f"R$ {total_gasto:.2f}")

                    # Total Desconto: Somatória dos valores do DB "compras_cabecalho[descontos]"
                    # Agora usando df_cabecalho para somar os descontos do cabeçalho
                    total_desconto = df_cabecalho["descontos"].sum()
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

                    # As colunas já vêm formatadas da RPC, basta renomear para exibição
                    # Removendo a coluna "desconto" da visualização da tabela
                    df_visualizacao = df_detalhadas.drop(columns=["desconto"], errors="ignore").rename(columns={
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
                    st.info("📭 Nenhuma compra encontrada no período selecionado.")
            else:
                st.error("❌ Erro ao buscar compras. Verifique a conexão com o banco de dados ou se há dados no período.")


