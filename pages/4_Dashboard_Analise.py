import streamlit as st
import pandas as pd
from services import db_queries
import datetime
import plotly.express as px

st.sidebar.title("Menu de Navegação")
st.sidebar.markdown("""GSproject""")

st.set_page_config(page_title="Dashboard de Análise", layout="wide")

st.title("📈 Dashboard de Análise de Compras")
st.write("Visualize suas compras com gráficos e estatísticas detalhadas.")

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
if st.button("🔍 Gerar Dashboard"):
	if data_inicio > data_fim:
		st.error("❌ A data de início deve ser menor ou igual à data de fim.")
	else:
		with st.spinner("Buscando dados para o dashboard..."):
			# Busca dados para estatísticas (cabeçalho)
			compras_cabecalho = db_queries.get_compras_cabecalho_periodo(data_inicio, data_fim)
			# Chama a função RPC para obter os dados detalhados para a tabela
			compras_detalhadas = db_queries.get_compras_detalhadas_rpc(data_inicio, data_fim)

			if compras_cabecalho and compras_detalhadas:
				df_cabecalho = pd.DataFrame(compras_cabecalho)
				df_detalhadas = pd.DataFrame(compras_detalhadas)

				if not df_cabecalho.empty and not df_detalhadas.empty:
					st.success(f"✅ Dados carregados para {len(df_detalhadas)} itens de compras no período selecionado!")

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
							st.subheader("📊 Estatísticas Detalhadas do Período")
							col1, col2, col3 = st.columns(3)

							total_gasto = df_detalhadas_filtrado["valor_total"].sum()
							with col1:
								st.metric("Total Gasto", f"R$ {total_gasto:.2f}")

							total_desconto = df_cabecalho_filtrado["descontos"].sum()
							with col2:
								st.metric("Total Desconto", f"R$ {total_desconto:.2f}")

							valor_final_pago = total_gasto - total_desconto
							with col3:
								st.metric("Valor Final Pago", f"R$ {valor_final_pago:.2f}")

							st.markdown("--- ")

							# ======================
							# Análises Gráficas
							# ======================
							st.subheader("📈 Análises Gráficas e Tendências")

							# Gráfico de Gastos por Mercado
							gastos_por_mercado = df_detalhadas_filtrado.groupby("mercado")["valor_total"].sum().reset_index()
							fig_mercado = px.bar(gastos_por_mercado, x="mercado", y="valor_total",
												 title="Gastos Totais por Mercado",
												 labels={"mercado": "Mercado", "valor_total": "Valor Gasto (R$)"})
							st.plotly_chart(fig_mercado, use_container_width=True)

							# Gráfico de Gastos por Data (Tendência)
							df_detalhadas_filtrado["data_compra"] = pd.to_datetime(df_detalhadas_filtrado["data_compra"])
							gastos_por_data = df_detalhadas_filtrado.groupby(df_detalhadas_filtrado["data_compra"].dt.date)["valor_total"].sum().reset_index()
							gastos_por_data.columns = ["Data da Compra", "Valor Gasto"]
							fig_data = px.line(gastos_por_data, x="Data da Compra", y="Valor Gasto",
											   title="Tendência de Gastos ao Longo do Tempo",
											   labels={"Data da Compra": "Data", "Valor Gasto": "Valor Gasto (R$)"})
							st.plotly_chart(fig_data, use_container_width=True)

							# Gráfico de Itens Mais Comprados
							itens_mais_comprados = df_detalhadas_filtrado.groupby("descricao")["quantidade"].sum().nlargest(10).reset_index()
							fig_itens = px.bar(itens_mais_comprados, x="descricao", y="quantidade",
											   title="Top 10 Itens Mais Comprados (por Quantidade)",
											   labels={"descricao": "Item", "quantidade": "Quantidade Total"})
							st.plotly_chart(fig_itens, use_container_width=True)

						else:
							st.info("📭 Nenhuma compra encontrada para os mercados selecionados no período.")
					else:
						st.info("Por favor, selecione ao menos um mercado para filtrar.")

				else:
					st.info("📭 Nenhuma compra encontrada no período selecionado.")
			else:
				st.error("❌ Erro ao buscar compras. Verifique a conexão com o banco de dados ou se há dados no período.")
