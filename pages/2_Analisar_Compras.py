import streamlit as st
import pandas as pd
from services import db_queries
from services.supabase_client import (
    require_authentication, 
    get_user_email, 
    get_user_id,
    get_user_data
)
import datetime
import plotly.express as px


st.sidebar.title("Menu de Navegação")
st.sidebar.markdown("GSproject")
user_email = get_user_email()
if user_email:
    st.sidebar.markdown(f"👤 **{user_email}**")

st.title("📊 Análise de Compras")
st.write("Visualize e analise suas compras pessoais de forma detalhada.")

st.write("Selecione o período para analisar suas compras:")

# Seleção de período
st.subheader("📅 Selecione o Período")
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
if st.button("🔍 Buscar Minhas Compras", type="primary"):
    if data_inicio > data_fim:
        st.error("❌ A data de início deve ser menor ou igual à data de fim.")
    else:
        with st.spinner("Buscando compras..."):
            # Busca dados para estatísticas (cabeçalho)
            try:
                compras_cabecalho = db_queries.get_compras_cabecalho_periodo(data_inicio, data_fim)
                # Chama a função RPC para obter os dados detalhados para a tabela
                compras_detalhadas = db_queries.get_compras_detalhadas_rpc(data_inicio, data_fim)

                if compras_cabecalho and compras_detalhadas:
                    df_cabecalho = pd.DataFrame(compras_cabecalho)
                    df_detalhadas = pd.DataFrame(compras_detalhadas)

                    if not df_cabecalho.empty and not df_detalhadas.empty:
                        st.success(f"✅ Encontrados {len(df_detalhadas)} itens de compras no período selecionado!")

                    # ======================
                    # Filtro de Mercado (corrigido: pega todos os mercados do cabeçalho)
                    # ======================
                    todos_mercados_db = db_queries.buscar_mercados()
                    df_todos_mercados = pd.DataFrame(todos_mercados_db)
                    mercados_ids_periodo = df_cabecalho["mercado_id"].unique().tolist()
                    mercados_disponiveis = df_todos_mercados[df_todos_mercados["id"].isin(mercados_ids_periodo)]["nome"].tolist()
                    # Guardar seleção no session_state para não resetar
                    if "mercados_selecionados" not in st.session_state:
                        st.session_state["mercados_selecionados"] = mercados_disponiveis
                    mercados_selecionados = st.multiselect(
                        "Filtrar por Mercado",
                        options=mercados_disponiveis,
                        default=st.session_state["mercados_selecionados"]
                    )
                    st.session_state["mercados_selecionados"] = mercados_selecionados

                    if mercados_selecionados:
                        df_detalhadas_filtrado = df_detalhadas[df_detalhadas["mercado"].isin(mercados_selecionados)]
                        # Para filtrar o cabeçalho, precisamos dos IDs dos mercados correspondentes
                        todos_mercados_db = db_queries.buscar_mercados()
                        df_todos_mercados = pd.DataFrame(todos_mercados_db)
                        mercado_ids_selecionados = df_todos_mercados[
                            df_todos_mercados["nome"].isin(mercados_selecionados)
                        ]["id"].tolist()
                        df_cabecalho_filtrado = df_cabecalho[
                            df_cabecalho["mercado_id"].isin(mercado_ids_selecionados)
                        ]

                        if not df_detalhadas_filtrado.empty:
                            # Tabela de visualização dos itens do período selecionado
                            st.subheader("📋 Itens do Período Selecionado")
                            df_visualizacao = df_detalhadas_filtrado.drop(columns=["desconto", "item"], errors="ignore").rename(columns={
                                "data_compra": "Data da Compra",
                                "descricao": "Descrição",
                                "quantidade": "Quantidade",
                                "unidade": "Unidade",
                                "valor_unitario": "Valor Unitário",
                                "valor_total": "Valor Total",
                                "mercado": "Mercado",
                                "cidade": "Cidade"
                            })
                            st.dataframe(df_visualizacao, use_container_width=True)

                            # ========== DASHBOARD LAYOUT ========== #
                            import numpy as np
                            # Gráficos 1 e 2 lado a lado
                            col_g1, col_g2 = st.columns(2)
                            # Gráfico: Itens com Maior Aumento de Preço
                            with col_g1:
                                st.subheader("Itens com Maior Aumento de Preço")
                                if "codigo" in df_detalhadas_filtrado.columns:
                                    group_cols = ["codigo", "descricao"]
                                else:
                                    group_cols = ["descricao"]
                                df_precos = df_detalhadas_filtrado.groupby(group_cols).agg(
                                    media=("valor_unitario", "mean"),
                                    maximo=("valor_unitario", "max"),
                                    minimo=("valor_unitario", "min"),
                                    count=("valor_unitario", "count")
                                ).reset_index()
                                df_precos["var_max"] = ((df_precos["maximo"] - df_precos["media"]) / df_precos["media"]) * 100
                                df_precos["var_min"] = ((df_precos["minimo"] - df_precos["media"]) / df_precos["media"]) * 100
                                df_aumento = df_precos[(df_precos["count"] > 1) & (df_precos["var_max"] > 0)]
                                df_aumento = df_aumento.sort_values("var_max", ascending=False).head(10)
                                fig_aumento = px.bar(
                                    df_aumento,
                                    x="var_max",
                                    y="descricao",
                                    orientation="h",
                                    labels={"var_max": "Variação (%)", "descricao": "Item"}
                                )
                                st.plotly_chart(fig_aumento, use_container_width=True, height=350)
                            # Gráfico: Itens com Maior Redução de Preço
                            with col_g2:
                                st.subheader("Itens com Maior Redução de Preço")
                                df_reducao = df_precos[(df_precos["count"] > 1) & (df_precos["var_min"] < 0)]
                                df_reducao = df_reducao.sort_values("var_min").head(10)
                                fig_reducao = px.bar(
                                    df_reducao,
                                    x="var_min",
                                    y="descricao",
                                    orientation="h",
                                    labels={"var_min": "Variação (%)", "descricao": "Item"}
                                )
                                st.plotly_chart(fig_reducao, use_container_width=True, height=350)

                            # Gráficos 3 e 4 lado a lado
                            col_g3, col_g4 = st.columns(2)
                            with col_g3:
                                st.subheader("Gasto Mensal")
                                df_cabecalho_filtrado["mes"] = pd.to_datetime(df_cabecalho_filtrado["data_compra"]).dt.strftime("%B/%Y")
                                df_cabecalho_filtrado = df_cabecalho_filtrado.sort_values("data_compra")
                                df_gasto_mensal = df_cabecalho_filtrado.groupby("mes", sort=False)["valor_final_pago"].sum().reset_index()
                                df_gasto_mensal["mes_ordem"] = pd.to_datetime(df_gasto_mensal["mes"], format="%B/%Y")
                                df_gasto_mensal = df_gasto_mensal.sort_values("mes_ordem")
                                fig_gasto_mensal = px.bar(
                                    df_gasto_mensal,
                                    x="mes",
                                    y="valor_final_pago",
                                    labels={"mes": "Mês", "valor_final_pago": "Valor total gasto"}
                                )
                                if len(df_gasto_mensal) >= 3:
                                    media_mensal = df_gasto_mensal["valor_final_pago"].mean()
                                    fig_gasto_mensal.add_hline(y=media_mensal, line_dash="dash", line_color="red", annotation_text="Média mensal", annotation_position="top left")
                                st.plotly_chart(fig_gasto_mensal, use_container_width=True, height=350)
                            with col_g4:
                                st.subheader("Tendência de Gastos (Regressão Linear)")
                                if not df_gasto_mensal.empty:
                                    meses_labels = df_gasto_mensal["mes"].tolist()
                                    df_gasto_mensal["mes_num"] = range(1, len(df_gasto_mensal) + 1)
                                    x = df_gasto_mensal["mes_num"].values.reshape(-1, 1)
                                    y = df_gasto_mensal["valor_final_pago"].values
                                    from sklearn.linear_model import LinearRegression
                                    model = LinearRegression()
                                    model.fit(x, y)
                                    x_pred = np.arange(1, len(df_gasto_mensal) + 7).reshape(-1, 1)
                                    y_pred = model.predict(x_pred)
                                    import calendar
                                    from datetime import datetime
                                    ult_mes = pd.to_datetime(df_gasto_mensal["mes"].iloc[-1], format="%B/%Y")
                                    proj_labels = []
                                    for i in range(1, 7):
                                        next_month = ult_mes + pd.DateOffset(months=i)
                                        proj_labels.append(next_month.strftime("%B/%Y"))
                                    x_labels = meses_labels + proj_labels
                                    fig_tend = px.line(
                                        x=x_labels[:len(y)],
                                        y=y,
                                        labels={"x": "Mês", "y": "Valor total gasto"}
                                    )
                                    fig_tend.add_scatter(
                                        x=x_labels[len(y):],
                                        y=y_pred[len(y):],
                                        mode="lines",
                                        line=dict(dash="dot", color="orange"),
                                        name="Projeção 6 meses"
                                    )
                                    st.plotly_chart(fig_tend, use_container_width=True, height=350)

                            # =====================
                            # ANÁLISE FINAL: Preço médio dos itens no período selecionado
                            # =====================
                            st.subheader("Preço Médio dos Itens no Período Selecionado")
                            df_media_itens = df_detalhadas_filtrado.groupby("descricao").agg(
                                media=("valor_unitario", "mean"),
                                maximo=("valor_unitario", "max"),
                                minimo=("valor_unitario", "min"),
                                qtd_registro=("valor_unitario", "count")
                            ).reset_index()
                            df_media_itens = df_media_itens.rename(columns={
                                "descricao": "Descrição", "media": "Média", "maximo": "Máx.", "minimo": "Mín.", "qtd_registro": "Qtd. Registro"
                            })
                            st.dataframe(
                                df_media_itens[["Descrição", "Média", "Máx.", "Mín.", "Qtd. Registro"]],
                                use_container_width=True
                            )
                        else:
                            st.info("📭 Nenhuma compra encontrada para os mercados selecionados no período.")
                    else:
                        st.info("Por favor, selecione ao menos um mercado para filtrar.")

                else:
                    st.info("📭 Nenhuma compra encontrada no período selecionado.")
            except Exception as e:
                if "schema cache" in str(e) or "not found" in str(e):
                    st.info("📭 Nenhuma compra registrada para este usuário no período selecionado.")
                else:
                    st.error(f"❌ Erro ao buscar compras: {e}")

# Rodapé
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666; font-size: 0.9em;'>"
    "🔒 Análise baseada apenas em suas compras pessoais | Protegido pela LGPD"
    "</div>", 
    unsafe_allow_html=True
)


