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
import plotly.graph_objects as go

st.set_page_config(page_title="Análise de Compras", layout="wide")

# Força autenticação
require_authentication()

# Configuração da sidebar
st.sidebar.title("🛒 Menu de Navegação")
st.sidebar.markdown("**GSproject**")
st.sidebar.markdown("---")
st.sidebar.markdown(f"👤 **{get_user_email()}**")

st.title("📊 Análise de Compras")
st.write("Visualize e analise suas compras pessoais de forma detalhada.")

# Informação sobre privacidade
st.info("🔒 **Privacidade:** Esta análise mostra apenas suas compras pessoais.")

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
        with st.spinner("Buscando suas compras..."):
            user_id = get_user_id()
            # Busca compras do usuário no período especificado
            try:
                from services.supabase_client import supabase
                response = supabase.table("compras_cabecalho").select("""
                    id,
                    data_compra,
                    valor_total,
                    descontos,
                    valor_final_pago,
                    mercado_id,
                    mercados(nome, cidade),
                    compras_itens(codigo, descricao, quantidade, unidade, valor_unitario, valor_total)
                """).gte("data_compra", data_inicio.strftime('%Y-%m-%d')).lte("data_compra", data_fim.strftime('%Y-%m-%d')).execute()

                if response.data:
                    compras_detalhadas = []
                    for compra in response.data:
                        mercado_nome = compra.get('mercados', {}).get('nome', 'N/A')
                        mercado_cidade = compra.get('mercados', {}).get('cidade', 'N/A')
                        itens = compra.get('compras_itens', [])
                        for item in itens:
                            compras_detalhadas.append({
                                'data_compra': compra['data_compra'],
                                'mercado': mercado_nome,
                                'cidade': mercado_cidade,
                                'codigo': item['codigo'],
                                'descricao': item['descricao'],
                                'quantidade': item['quantidade'],
                                'unidade': item['unidade'],
                                'valor_unitario': item['valor_unitario'],
                                'valor_total': item['valor_total'],
                                'compra_valor_total': compra['valor_total'],
                                'compra_desconto': compra['descontos'],
                                'compra_valor_final': compra['valor_final_pago']
                            })
                    if compras_detalhadas:
                        df_detalhadas = pd.DataFrame(compras_detalhadas)
                        df_detalhadas['data_compra'] = pd.to_datetime(df_detalhadas['data_compra'])
                        st.success(f"✅ Encontrados {len(df_detalhadas)} itens em suas compras no período selecionado!")

                        # ======================
                        # Filtro de Mercado
                        # ======================
                        st.subheader("🏪 Filtros")
                        mercados_disponiveis = df_detalhadas["mercado"].unique().tolist()
                        mercados_selecionados = st.multiselect(
                            "Filtrar por Mercado",
                            options=mercados_disponiveis,
                            default=mercados_disponiveis
                        )
                        if mercados_selecionados:
                            df_filtrado = df_detalhadas[df_detalhadas["mercado"].isin(mercados_selecionados)]
                            if not df_filtrado.empty:
                                st.subheader("📊 Resumo do Período")
                                total_gasto = df_filtrado['compra_valor_final'].sum()
                                total_compras = df_filtrado['data_compra'].nunique()
                                total_itens = len(df_filtrado)
                                ticket_medio = total_gasto / total_compras if total_compras > 0 else 0
                                col1, col2, col3, col4 = st.columns(4)
                                with col1:
                                    st.metric("💰 Total Gasto", f"R$ {total_gasto:.2f}")
                                with col2:
                                    st.metric("🛒 Compras Realizadas", total_compras)
                                with col3:
                                    st.metric("📦 Itens Comprados", total_itens)
                                with col4:
                                    st.metric("🎯 Ticket Médio", f"R$ {ticket_medio:.2f}")
                                st.subheader("📈 Análises Visuais")
                                tab1, tab2, tab3 = st.tabs(["💰 Gastos por Mercado", "📅 Gastos ao Longo do Tempo", "🏆 Top Itens"])
                                with tab1:
                                    gastos_mercado = df_filtrado.groupby('mercado')['compra_valor_final'].sum().reset_index()
                                    fig_mercado = px.pie(gastos_mercado, values='compra_valor_final', names='mercado', 
                                                       title="Distribuição de Gastos por Mercado")
                                    st.plotly_chart(fig_mercado, use_container_width=True)
                                with tab2:
                                    gastos_tempo = df_filtrado.groupby('data_compra')['compra_valor_final'].sum().reset_index()
                                    fig_tempo = px.line(gastos_tempo, x='data_compra', y='compra_valor_final',
                                                      title="Evolução dos Gastos ao Longo do Tempo",
                                                      labels={'data_compra': 'Data', 'compra_valor_final': 'Valor (R$)'})
                                    st.plotly_chart(fig_tempo, use_container_width=True)
                                with tab3:
                                    top_itens = df_filtrado.groupby('descricao')['valor_total'].sum().sort_values(ascending=False).head(10)
                                    fig_itens = px.bar(x=top_itens.values, y=top_itens.index, orientation='h',
                                                     title="Top 10 Itens por Valor Total Gasto",
                                                     labels={'x': 'Valor Total (R$)', 'y': 'Item'})
                                    st.plotly_chart(fig_itens, use_container_width=True)
                                st.subheader("📋 Detalhes das Compras")
                                df_visualizacao = df_filtrado.drop(columns=["compra_valor_total", "compra_desconto", "compra_valor_final"], errors="ignore").rename(columns={
                                    "data_compra": "Data da Compra",
                                    "codigo": "Código",
                                    "descricao": "Descrição",
                                    "quantidade": "Quantidade",
                                    "unidade": "Unidade",
                                    "valor_unitario": "Valor Unitário (R$)",
                                    "valor_total": "Valor Total (R$)",
                                    "mercado": "Mercado",
                                    "cidade": "Cidade"
                                })
                                df_visualizacao["Valor Unitário (R$)"] = df_visualizacao["Valor Unitário (R$)"].apply(lambda x: f"R$ {x:.2f}")
                                df_visualizacao["Valor Total (R$)"] = df_visualizacao["Valor Total (R$)"].apply(lambda x: f"R$ {x:.2f}")
                                df_visualizacao["Data da Compra"] = pd.to_datetime(df_visualizacao["Data da Compra"]).dt.strftime('%d/%m/%Y')
                                st.dataframe(df_visualizacao, use_container_width=True)
                                csv = df_visualizacao.to_csv(index=False, sep=";")
                                st.download_button(
                                    label="📥 Download CSV",
                                    data=csv,
                                    file_name=f"minhas_compras_{data_inicio}_{data_fim}.csv",
                                    mime="text/csv"
                                )
                            else:
                                st.info("📭 Nenhuma compra encontrada para os mercados selecionados no período.")
                        else:
                            st.info("Por favor, selecione ao menos um mercado para filtrar.")
                    else:
                        st.info("📭 Você ainda não possui compras registradas no período selecionado.")
                        st.markdown("---")
                        st.info("💡 **Dica:** Registre suas primeiras compras para começar a analisar seus gastos!")
                        if st.button("📝 Ir para Registrar Compras"):
                            st.switch_page("pages/1_Registrar_Compras.py")
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


