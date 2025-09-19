import streamlit as st
import pandas as pd
from services import db_queries
from services.supabase_client import (
    require_authentication, 
    get_user_email, 
    get_user_id,
    is_admin_user
)
import datetime
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="Dashboard de Análise", layout="wide")

# Força autenticação
require_authentication()

# Configuração da sidebar
st.sidebar.title("🛒 Menu de Navegação")
st.sidebar.markdown("**GSproject**")
st.sidebar.markdown("---")
user_email = get_user_email()
is_admin = is_admin_user()
st.sidebar.markdown(f"👤 **{user_email}**")
if is_admin:
    st.sidebar.success("🔑 **Administrador**")

st.title("📈 Dashboard de Análise de Compras")

if is_admin:
    st.info("🔑 **Modo Administrador:** Você pode visualizar dados agregados do sistema (sem dados pessoais de usuários).")
    st.write("Visualize estatísticas gerais e tendências do sistema.")
else:
    st.write("Visualize suas compras pessoais com gráficos e estatísticas detalhadas.")
    st.info("🔒 **Privacidade:** Este dashboard mostra apenas suas compras pessoais.")

# Seleção de período
st.subheader("📅 Período de Análise")
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
if st.button("📊 Gerar Dashboard", type="primary"):
    if data_inicio > data_fim:
        st.error("❌ A data de início deve ser menor ou igual à data de fim.")
    else:
        with st.spinner("Carregando dados do dashboard..."):
            user_id = get_user_id()
            
            try:
                from services.supabase_client import supabase
                
                if is_admin:
                    # Para admin: dados agregados sem informações pessoais
                    st.subheader("📊 Estatísticas Gerais do Sistema")
                    
                    # Busca dados agregados
                    response = supabase.table("compras_cabecalho").select("""
                        data_compra,
                        valor_total,
                        valor_final_pago,
                        mercado_id,
                        mercados(nome, cidade)
                    """).gte("data_compra", data_inicio.strftime('%Y-%m-%d')).lte("data_compra", data_fim.strftime('%Y-%m-%d')).execute()
                    
                    if response.data:
                        compras_admin = []
                        for compra in response.data:
                            compras_admin.append({
                                'data_compra': compra['data_compra'],
                                'valor_total': compra['valor_total'],
                                'valor_final_pago': compra['valor_final_pago'],
                                'mercado': compra['mercados']['nome'] if compra['mercados'] else 'N/A'
                            })
                        
                        df_admin = pd.DataFrame(compras_admin)
                        df_admin['data_compra'] = pd.to_datetime(df_admin['data_compra'])
                        
                        # Métricas gerais
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("💰 Volume Total", f"R$ {df_admin['valor_final_pago'].sum():.2f}")
                        with col2:
                            st.metric("🛒 Total de Compras", len(df_admin))
                        with col3:
                            st.metric("🏪 Mercados Ativos", df_admin['mercado'].nunique())
                        with col4:
                            st.metric("🎯 Ticket Médio", f"R$ {df_admin['valor_final_pago'].mean():.2f}")
                        
                        # Gráficos para admin
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            # Volume por mercado
                            volume_mercado = df_admin.groupby('mercado')['valor_final_pago'].sum().reset_index()
                            fig_admin_mercado = px.pie(volume_mercado, values='valor_final_pago', names='mercado',
                                                     title="Volume de Vendas por Mercado")
                            st.plotly_chart(fig_admin_mercado, use_container_width=True)
                        
                        with col2:
                            # Tendência temporal
                            volume_tempo = df_admin.groupby(df_admin['data_compra'].dt.date)['valor_final_pago'].sum().reset_index()
                            fig_admin_tempo = px.line(volume_tempo, x='data_compra', y='valor_final_pago',
                                                    title="Evolução do Volume de Vendas")
                            st.plotly_chart(fig_admin_tempo, use_container_width=True)
                    
                    else:
                        st.info("📭 Nenhum dado encontrado no período selecionado.")
                
                else:
                    # Para usuários normais: dados pessoais
                    # Query para buscar compras detalhadas do usuário
                    response = supabase.table("compras_cabecalho").select("""
                        id,
                        data_compra,
                        valor_total,
                        descontos,
                        valor_final_pago,
                        mercado_id,
                        mercados(nome, cidade),
                        compras_itens(codigo, descricao, quantidade, unidade, valor_unitario, valor_total)
                    """).eq("user_id", user_id).gte("data_compra", data_inicio.strftime('%Y-%m-%d')).lte("data_compra", data_fim.strftime('%Y-%m-%d')).execute()

                    if response.data:
                        # Processa os dados
                        compras_detalhadas = []
                        compras_resumo = []
                        
                        for compra in response.data:
                            mercado_nome = compra.get('mercados', {}).get('nome', 'N/A')
                            mercado_cidade = compra.get('mercados', {}).get('cidade', 'N/A')
                            # Dados resumo da compra
                            compras_resumo.append({
                                'data_compra': compra['data_compra'],
                                'mercado': mercado_nome,
                                'valor_total': compra['valor_total'],
                                'descontos': compra['descontos'],
                                'valor_final_pago': compra['valor_final_pago']
                            })
                            # Dados detalhados dos itens
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
                                    'valor_total': item['valor_total']
                                })
                        
                        if compras_detalhadas:
                            df_detalhadas = pd.DataFrame(compras_detalhadas)
                            df_resumo = pd.DataFrame(compras_resumo)
                            df_detalhadas['data_compra'] = pd.to_datetime(df_detalhadas['data_compra'])
                            df_resumo['data_compra'] = pd.to_datetime(df_resumo['data_compra'])
                            
                            st.success(f"✅ Dashboard gerado com {len(df_detalhadas)} itens de suas compras!")

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
                                df_resumo_filtrado = df_resumo[df_resumo["mercado"].isin(mercados_selecionados)]
                                
                                if not df_filtrado.empty:
                                    # ======================
                                    # Métricas Principais
                                    # ======================
                                    st.subheader("📊 Resumo Financeiro")
                                    
                                    total_gasto = df_resumo_filtrado['valor_final_pago'].sum()
                                    total_compras = len(df_resumo_filtrado)
                                    total_itens = len(df_filtrado)
                                    ticket_medio = total_gasto / total_compras if total_compras > 0 else 0
                                    total_desconto = df_resumo_filtrado['descontos'].sum()
                                    
                                    col1, col2, col3, col4, col5 = st.columns(5)
                                    with col1:
                                        st.metric("💰 Total Gasto", f"R$ {total_gasto:.2f}")
                                    with col2:
                                        st.metric("🛒 Compras", total_compras)
                                    with col3:
                                        st.metric("📦 Itens", total_itens)
                                    with col4:
                                        st.metric("🎯 Ticket Médio", f"R$ {ticket_medio:.2f}")
                                    with col5:
                                        st.metric("🏷️ Descontos", f"R$ {total_desconto:.2f}")

                                    # ======================
                                    # Análises Gráficas
                                    # ======================
                                    st.subheader("📈 Análises Visuais")

                                    # Tabs para diferentes análises
                                    tab1, tab2, tab3, tab4 = st.tabs(["💰 Gastos", "📅 Tendências", "🏆 Top Itens", "🏪 Mercados"])
                                    
                                    with tab1:
                                        # Gráfico de gastos por categoria
                                        col1, col2 = st.columns(2)
                                        
                                        with col1:
                                            # Gastos por mercado
                                            gastos_mercado = df_resumo_filtrado.groupby('mercado')['valor_final_pago'].sum().reset_index()
                                            fig_mercado = px.pie(gastos_mercado, values='valor_final_pago', names='mercado',
                                                               title="Distribuição de Gastos por Mercado")
                                            st.plotly_chart(fig_mercado, use_container_width=True)
                                        
                                        with col2:
                                            # Comparação valor total vs valor pago
                                            comparacao = df_resumo_filtrado[['valor_total', 'valor_final_pago']].sum()
                                            fig_comparacao = go.Figure(data=[
                                                go.Bar(name='Valor Total', x=['Compras'], y=[comparacao['valor_total']]),
                                                go.Bar(name='Valor Pago', x=['Compras'], y=[comparacao['valor_final_pago']])
                                            ])
                                            fig_comparacao.update_layout(title="Valor Total vs Valor Pago (com descontos)")
                                            st.plotly_chart(fig_comparacao, use_container_width=True)
                                    
                                    with tab2:
                                        # Tendências temporais
                                        gastos_tempo = df_resumo_filtrado.groupby(df_resumo_filtrado['data_compra'].dt.date)['valor_final_pago'].sum().reset_index()
                                        fig_tempo = px.line(gastos_tempo, x='data_compra', y='valor_final_pago',
                                                          title="Evolução dos Gastos ao Longo do Tempo",
                                                          labels={'data_compra': 'Data', 'valor_final_pago': 'Valor (R$)'})
                                        fig_tempo.update_traces(mode='lines+markers')
                                        st.plotly_chart(fig_tempo, use_container_width=True)
                                        
                                        # Gastos por dia da semana
                                        df_filtrado['dia_semana'] = df_filtrado['data_compra'].dt.day_name()
                                        gastos_dia_semana = df_filtrado.groupby('dia_semana')['valor_total'].sum().reset_index()
                                        fig_dia_semana = px.bar(gastos_dia_semana, x='dia_semana', y='valor_total',
                                                              title="Gastos por Dia da Semana")
                                        st.plotly_chart(fig_dia_semana, use_container_width=True)
                                    
                                    with tab3:
                                        col1, col2 = st.columns(2)
                                        
                                        with col1:
                                            # Top itens por valor
                                            top_itens_valor = df_filtrado.groupby('descricao')['valor_total'].sum().sort_values(ascending=False).head(10)
                                            fig_itens_valor = px.bar(x=top_itens_valor.values, y=top_itens_valor.index, orientation='h',
                                                                   title="Top 10 Itens por Valor Gasto")
                                            st.plotly_chart(fig_itens_valor, use_container_width=True)
                                        
                                        with col2:
                                            # Top itens por quantidade
                                            top_itens_qtd = df_filtrado.groupby('descricao')['quantidade'].sum().sort_values(ascending=False).head(10)
                                            fig_itens_qtd = px.bar(x=top_itens_qtd.values, y=top_itens_qtd.index, orientation='h',
                                                                 title="Top 10 Itens por Quantidade")
                                            st.plotly_chart(fig_itens_qtd, use_container_width=True)
                                    
                                    with tab4:
                                        # Análise por mercados
                                        mercado_stats = df_resumo_filtrado.groupby('mercado').agg({
                                            'valor_final_pago': ['sum', 'mean', 'count']
                                        }).round(2)
                                        mercado_stats.columns = ['Total Gasto', 'Ticket Médio', 'Número de Compras']
                                        mercado_stats = mercado_stats.reset_index()
                                        
                                        st.subheader("📊 Estatísticas por Mercado")
                                        st.dataframe(mercado_stats, use_container_width=True)
                                        
                                        # Gráfico de frequência de compras por mercado
                                        fig_freq = px.bar(mercado_stats, x='mercado', y='Número de Compras',
                                                        title="Frequência de Compras por Mercado")
                                        st.plotly_chart(fig_freq, use_container_width=True)

                                else:
                                    st.info("📭 Nenhuma compra encontrada para os mercados selecionados no período.")
                            else:
                                st.info("Por favor, selecione ao menos um mercado para filtrar.")

                        else:
                            st.info("📭 Você ainda não possui compras registradas no período selecionado.")
                            
                            # Sugestão para registrar compras
                            st.markdown("---")
                            st.info("💡 **Dica:** Registre suas primeiras compras para começar a visualizar seu dashboard!")
                            if st.button("📝 Ir para Registrar Compras"):
                                st.switch_page("pages/1_Registrar_Compras.py")
                    else:
                        st.info("📭 Nenhuma compra encontrada no período selecionado.")

            except Exception as e:
                if "schema cache" in str(e) or "not found" in str(e):
                    st.info("📭 Nenhuma compra registrada para este usuário no período selecionado.")
                else:
                    st.error(f"❌ Erro ao gerar dashboard: {e}")

# Rodapé
st.markdown("---")
if is_admin:
    st.markdown(
        "<div style='text-align: center; color: #666; font-size: 0.9em;'>"
        "🔑 Dashboard Administrativo - Dados agregados sem informações pessoais"
        "</div>", 
        unsafe_allow_html=True
    )
else:
    st.markdown(
        "<div style='text-align: center; color: #666; font-size: 0.9em;'>"
        "🔒 Dashboard baseado apenas em suas compras pessoais | Protegido pela LGPD"
        "</div>", 
        unsafe_allow_html=True
    )


