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
            compras = db_queries.get_compras_periodo(data_inicio, data_fim)

            if compras:
                # Converte para DataFrame
                df = pd.DataFrame(compras)

                if not df.empty:
                    st.success(f"✅ Encontradas {len(df)} compras no período selecionado!")

                    # ======================
                    # Estatísticas
                    # ======================
                    st.subheader("📈 Estatísticas do Período")
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        total_gasto = df["valor_total"].sum()
                        st.metric("Total Gasto", f"R$ {total_gasto:.2f}")

                    descontos_unicos = df["descontos"].sum()
                    with col2:
                        st.metric("Total Descontos", f"R$ {descontos_unicos:.2f}")

                    valor_final = df["valor_final_pago"].sum()
                    with col3:
                        st.metric("Valor Final Pago", f"R$ {valor_final:.2f}")

                    # ======================
                    # Tabela de Compras
                    # ======================
                    st.subheader("📋 Compras do Período")

                    # Renomear colunas para visualização mais amigável
                    df_visualizacao = df.rename(columns={
                        "data_compra": "Data da Compra",
                        "valor_total": "Valor Total",
                        "descontos": "Descontos",
                        "valor_final_pago": "Valor Final Pago"
                    })

                    # Remover colunas técnicas
                    colunas_ocultas = ["id", "mercado_id", "created_at"]
                    df_visualizacao = df_visualizacao.drop(columns=colunas_ocultas, errors="ignore")

                    st.dataframe(df_visualizacao, use_container_width=True)

                    # ======================
                    # Download dos Dados
                    # ======================
                    csv = df_visualizacao.to_csv(index=False, sep=";")
                    st.download_button(
                        label="📥 Download CSV",
                        data=csv,
                        file_name=f"compras_{data_inicio}_{data_fim}.csv",
                        mime="text/csv"
                    )

                else:
                    st.info("📭 Nenhuma compra encontrada no período selecionado.")
            else:
                st.error("❌ Erro ao buscar compras. Verifique a conexão com o banco de dados.")
