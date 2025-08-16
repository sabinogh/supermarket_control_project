import pdfplumber
import pandas as pd
import requests
import urllib3
import streamlit as st
from dotenv import load_dotenv
import datetime
import json
import re

# Desabilitar avisos de SSL para desenvolvimento
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Carregar variáveis de ambiente
load_dotenv()

# Supabase Configuration
SUPABASE_URL = "https://wufmrqnmzcykiytqynhv.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind1Zm1ycW5temN5a2l5dHF5bmh2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTUyNTk2NzUsImV4cCI6MjA3MDgzNTY3NX0.lx44jf873UGPZZnCruSbEMLnnn8ya8N3dsXji_8w3YA"

# Headers para autenticação Supabase
headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

def test_supabase_connection():
    """Testa a conexão com o Supabase"""
    try:
        # Tenta fazer uma consulta simples na tabela de cabeçalho
        url = f"{SUPABASE_URL}/rest/v1/compras_cabecalho?select=id&limit=1"
        response = requests.get(url, headers=headers, verify=False)
        
        if response.status_code == 200:
            return True
        else:
            return False
    except Exception as e:
        return False

def buscar_compras_por_periodo(data_inicio, data_fim):
    """Busca compras no Supabase por período usando JOIN entre as tabelas"""
    try:
        # Converter datas para formato ISO
        data_inicio_iso = data_inicio.strftime("%Y-%m-%d")
        data_fim_iso = data_fim.strftime("%Y-%m-%d")
        
        # Buscar cabeçalhos das compras no período
        url_cabecalho = f"{SUPABASE_URL}/rest/v1/compras_cabecalho"
        params_cabecalho = [
            ("select", "*"),
            ("data_compra", f"gte.{data_inicio_iso}"),
            ("data_compra", f"lte.{data_fim_iso}"),
            ("order", "data_compra.desc"),
        ]
        
        response_cabecalho = requests.get(url_cabecalho, headers=headers, params=params_cabecalho, verify=False)
        response_cabecalho.raise_for_status()
        
        cabecalhos = response_cabecalho.json()
        
        # Para cada cabeçalho, buscar os itens correspondentes
        compras_completas = []
        
        for cabecalho in cabecalhos:
            compra_id = cabecalho['id']
            
            # Buscar itens desta compra
            url_itens = f"{SUPABASE_URL}/rest/v1/compras_itens"
            params_itens = [
                ("select", "*"),
                ("compra_id", f"eq.{compra_id}"),
                ("order", "id"),
            ]
            
            response_itens = requests.get(url_itens, headers=headers, params=params_itens, verify=False)
            response_itens.raise_for_status()
            
            itens = response_itens.json()
            
            # Combinar cabeçalho com itens
            for item in itens:
                compra_completa = {
                    "id": item['id'],
                    "compra_id": compra_id,
                    "data_compra": cabecalho['data_compra'],
                    "nome_mercado": cabecalho['nome_mercado'],
                    "cidade": cabecalho['cidade'],
                    "codigo": item['codigo'],
                    "descricao": item['descricao'],
                    "quantidade": item['quantidade'],
                    "unidade": item['unidade'],
                    "valor_unitario": item['valor_unitario'],
                    "valor_total": item['valor_total'],
                    "descontos": cabecalho['descontos'],
                    "valor_final_pago": cabecalho['valor_final_pago']
                }
                compras_completas.append(compra_completa)
        
        # Simular estrutura similar ao Notion para compatibilidade
        return {"results": compras_completas}
        
    except Exception as e:
        st.error(f"Erro ao buscar compras: {e}")
        return None

def processar_dados_compras(dados_supabase):
    """Processa os dados retornados pelo Supabase para exibição em tabela"""
    if not dados_supabase or "results" not in dados_supabase:
        return pd.DataFrame()
    
    compras_processadas = []
    
    for resultado in dados_supabase["results"]:
        # Dados já vêm em formato simples do Supabase
        compras_processadas.append({
            "Data da Compra": resultado.get("data_compra", ""),
            "Mercado": resultado.get("nome_mercado", ""),
            "Cidade": resultado.get("cidade", ""),
            "Item": resultado.get("id", ""),
            "Código": resultado.get("codigo", ""),
            "Descrição": resultado.get("descricao", ""),
            "Quantidade": resultado.get("quantidade", ""),
            "Unidade": resultado.get("unidade", ""),
            "Valor Unitário": resultado.get("valor_unitario", ""),
            "Valor Total": resultado.get("valor_total", ""),
            "Descontos": resultado.get("descontos", ""),
            "Valor Final Pago": resultado.get("valor_final_pago", "")
        })
    
    return pd.DataFrame(compras_processadas)

def create_supabase_page(item_data, compra_info):
    """Cria uma nova entrada no Supabase usando estrutura normalizada"""
    try:
        # Formatar a data para o formato ISO
        data_compra = compra_info["data_compra"]
        if isinstance(data_compra, str):
            # Se já é string, converter para datetime
            data_compra = datetime.datetime.strptime(data_compra, '%d/%m/%Y')
        data_iso = data_compra.strftime("%Y-%m-%d")

        # Adicionar header para retornar dados inseridos (sempre definir)
        headers_with_return = headers.copy()
        headers_with_return["Prefer"] = "return=representation"

        # Primeiro, criar o cabeçalho da compra (se não existir)
        url_check = f"{SUPABASE_URL}/rest/v1/compras_cabecalho"
        params_check = [
            ("select", "id"),
            ("data_compra", f"eq.{data_iso}"),
            ("nome_mercado", f"eq.{compra_info['nome_mercado']}"),
            ("cidade", f"eq.{compra_info['cidade']}"),
        ]

        response_check = requests.get(url_check, headers=headers, params=params_check, verify=False)
        compra_id = None

        if response_check.status_code == 200 and response_check.json():
            # Cabeçalho já existe, usar o ID existente
            compra_id = response_check.json()[0]['id']
        else:
            # Criar novo cabeçalho
            cabecalho_data = {
                "data_compra": data_iso,
                "nome_mercado": compra_info["nome_mercado"],
                "cidade": compra_info["cidade"],
                "valor_total": compra_info["valor_total"],
                "descontos": compra_info["descontos"],
                "valor_final_pago": compra_info["valor_final_pago"]
            }
            response_cabecalho = requests.post(
                f"{SUPABASE_URL}/rest/v1/compras_cabecalho", 
                headers=headers_with_return, 
                json=cabecalho_data, 
                verify=False
            )
            if response_cabecalho.status_code in [200, 201]:
                try:
                    cabecalho_response = response_cabecalho.json()
                    if cabecalho_response and isinstance(cabecalho_response, list) and len(cabecalho_response) > 0:
                        compra_id = cabecalho_response[0]['id']
                    elif cabecalho_response and isinstance(cabecalho_response, dict):
                        compra_id = cabecalho_response.get('id')
                except:
                    # Se não conseguir extrair ID, tentar buscar novamente
                    response_check = requests.get(url_check, headers=headers, params=params_check, verify=False)
                    if response_check.status_code == 200 and response_check.json():
                        compra_id = response_check.json()[0]['id']

        if not compra_id:
            st.error("❌ Não foi possível criar ou encontrar o cabeçalho da compra")
            return None
        
        # Agora inserir o item na tabela de itens
        item_data_normalized = {
            "compra_id": compra_id,
            "codigo": item_data["codigo"],
            "descricao": item_data["descricao"],
            "quantidade": item_data["quantidade"],
            "unidade": item_data["unidade"],
            "valor_unitario": item_data["valor_unitario"],
            "valor_total": item_data["valor_total"]
        }
        
        # Inserir item
        url_item = f"{SUPABASE_URL}/rest/v1/compras_itens"
        response_item = requests.post(url_item, headers=headers_with_return, json=item_data_normalized, verify=False)
        
        if response_item.status_code in [200, 201]:
            try:
                response_data = response_item.json()
                if response_data and isinstance(response_data, list) and len(response_data) > 0:
                    return response_data[0]
                elif response_data and isinstance(response_data, dict):
                    return response_data
                else:
                    return {"id": "created", "status": "success", "compra_id": compra_id}
            except (ValueError, json.JSONDecodeError) as json_error:
                if response_item.status_code in [200, 201]:
                    return {"id": "created", "status": "success", "compra_id": compra_id, "note": "no_json_response"}
                else:
                    raise json_error
        else:
            response_item.raise_for_status()
            
    except requests.exceptions.RequestException as e:
        st.error(f"Erro na requisição para o Supabase: {e}")
        return None
    except Exception as e:
        st.error(f"Erro ao criar entrada no Supabase: {e}")
        return None

st.set_page_config(page_title="Controle de Gastos Supermercado", layout="centered")

# Inicializar session state
if "pagina_atual" not in st.session_state:
    st.session_state.pagina_atual = "inicial"

# Função para voltar à página inicial
def voltar_inicial():
    st.session_state.pagina_atual = "inicial"
    st.rerun()

# Página inicial
if st.session_state.pagina_atual == "inicial":
    st.title("Controle de Gastos de Supermercado 🛒")
    st.write("""
    Bem-vindo ao sistema de controle de gastos de supermercado!
    Escolha uma das opções abaixo para começar.
    """)
    
    # Botão para testar conexão com Supabase
    if st.button("🔗 Testar Conexão com Supabase"):
        st.write("Testando conexão com o banco de dados do Supabase...")
        if test_supabase_connection():
            st.success("✅ Conexão com Supabase estabelecida com sucesso!")
        else:
            st.error("❌ Erro na conexão com Supabase. Verifique as credenciais.")
    
    # Botões principais
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 Analisar Compras", use_container_width=True):
            st.session_state.pagina_atual = "analisar"
            st.rerun()
    
    with col2:
        if st.button("📝 Registrar Compra", use_container_width=True):
            st.session_state.pagina_atual = "registrar"
            st.rerun()

# Página de análise de compras
elif st.session_state.pagina_atual == "analisar":
    st.title("📊 Análise de Compras")
    
    # Botão para voltar
    if st.button("← Voltar"):
        voltar_inicial()
    
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
                dados_compras = buscar_compras_por_periodo(data_inicio, data_fim)
                
                if dados_compras:
                    df_compras = processar_dados_compras(dados_compras)
                    
                    if not df_compras.empty:
                        st.success(f"✅ Encontradas {len(df_compras)} compras no período selecionado!")
                        
                        # Estatísticas
                        st.subheader("📈 Estatísticas do Período")
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            total_gasto = df_compras["Valor Total"].sum()
                            st.metric("Total Gasto", f"R$ {total_gasto:.2f}")
                        
                        with col2:
                            total_descontos = df_compras["Descontos"].sum()
                            st.metric("Total Descontos", f"R$ {total_descontos:.2f}")
                        
                        with col3:
                            valor_final = df_compras["Valor Final Pago"].sum()
                            st.metric("Valor Final", f"R$ {valor_final:.2f}")
                        
                        # Tabela de compras
                        st.subheader("📋 Compras do Período")
                        st.dataframe(df_compras, use_container_width=True)
                        
                        # Download dos dados
                        csv = df_compras.to_csv(index=False)
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

# Página de registro de compra
elif st.session_state.pagina_atual == "registrar":
    st.title("📝 Registrar Nova Compra")
    
    # Botão para voltar
    if st.button("← Voltar"):
        voltar_inicial()
    
    # Inicializar modo de registro
    if "modo_registro" not in st.session_state:
        st.session_state.modo_registro = "upload"
    
    # Botão para alternar entre upload e registro manual
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📄 Upload PDF", use_container_width=True, type="primary" if st.session_state.modo_registro == "upload" else "secondary"):
            st.session_state.modo_registro = "upload"
            st.rerun()
    with col2:
        if st.button("✏️ Registro Manual", use_container_width=True, type="primary" if st.session_state.modo_registro == "manual" else "secondary"):
            st.session_state.modo_registro = "manual"
            st.rerun()
    
    # Modo Upload PDF
    if st.session_state.modo_registro == "upload":
        st.write("Faça o upload da sua nota fiscal em PDF para começar a registrar sua compra.")

        colunas_itens = ["Item", "Código", "Descrição", "Quantidade", "Unidade", "Valor Unitário", "Valor Total"]

        def extrair_itens_nota(texto):
            # Regex para identificar blocos de itens (duas linhas por item)
            padrao_item = re.compile(r"(.+?) \(Código: (\d+) \) Vl\. Total\s*\nQtde\.:([\d,.]+) UN: (\w+) Vl\. Unit\.: ([\d,.]+) ([\d,.]+)")
            itens_tabela = []
            itens_supabase = []
            
            for i, match in enumerate(padrao_item.finditer(texto), 1):
                descricao = match.group(1).strip()
                codigo = match.group(2).strip()
                quantidade = match.group(3).replace(",", ".")
                unidade = match.group(4).strip()
                valor_unit = match.group(5).replace(",", ".")
                valor_total = match.group(6).replace(",", ".")
                
                # Dados para exibição na tabela
                itens_tabela.append([
                    i,
                    codigo,
                    descricao,
                    float(quantidade),
                    unidade,
                    float(valor_unit),
                    float(valor_total)
                ])
                
                # Dados para envio ao Supabase (dicionário)
                itens_supabase.append({
                    "item": i,
                    "codigo": codigo,
                    "descricao": descricao,
                    "quantidade": float(quantidade),
                    "unidade": unidade,
                    "valor_unitario": float(valor_unit),
                    "valor_total": float(valor_total)
                })
            
            return itens_tabela, itens_supabase

        uploaded_file = st.file_uploader("Faça upload da sua nota fiscal (PDF)", type=["pdf"])

        if uploaded_file is not None:
            st.success(f"Arquivo '{uploaded_file.name}' enviado com sucesso!")
            try:
                with pdfplumber.open(uploaded_file) as pdf:
                    texto = ""
                    for page in pdf.pages:
                        texto += page.extract_text() + "\n"
                itens_tabela, itens_supabase = extrair_itens_nota(texto)
                if itens_tabela:
                    df_itens = pd.DataFrame(itens_tabela, columns=colunas_itens)
                    st.subheader("📦 Itens da Compra (extraído do PDF)")
                    st.dataframe(df_itens)

                    # Sugestão de valor total lido dos itens
                    valor_total_lido = df_itens["Valor Total"].sum()

                    st.subheader("Adicionar Informações da Nota Fiscal Manualmente")
                    with st.form("form_nota_manual", clear_on_submit=False):
                        nome_mercado = st.text_input("Nome do Mercado")
                        cidade = st.text_input("Cidade")
                        data_compra = st.date_input("Data da Compra", value=datetime.date.today())
                        valor_total = st.number_input("Valor Total", value=float(valor_total_lido), format="%.2f")
                        descontos = st.number_input("Descontos", value=0.0, format="%.2f")
                        valor_final_pago = valor_total - descontos

                        submitted = st.form_submit_button("Adicionar")

                    # Se clicou em Adicionar, salva os dados no session_state para confirmação
                    if submitted and not st.session_state.get("compra_confirmada", False):
                        st.session_state["dados_para_confirmar"] = {
                            "nome_mercado": nome_mercado,
                            "cidade": cidade,
                            "data_compra": data_compra,
                            "valor_total": valor_total,
                            "descontos": descontos,
                            "valor_final_pago": valor_final_pago
                        }

                    # Se há dados para confirmar e ainda não confirmou a compra, mostra a confirmação
                    if (
                        st.session_state.get("dados_para_confirmar")
                        and not st.session_state.get("compra_confirmada", False)
                    ):
                        dados = st.session_state["dados_para_confirmar"]
                        data_compra_str = dados["data_compra"].strftime('%d/%m/%Y')
                        st.info(f"Confirme os dados abaixo antes de adicionar:")
                        st.write(f"**Nome Mercado:** {dados['nome_mercado']}")
                        st.write(f"**Cidade:** {dados['cidade']}")
                        st.write(f"**Data Compra:** {data_compra_str}")
                        st.write(f"**Valor Total:** R$ {dados['valor_total']:.2f}")
                        st.write(f"**Descontos:** R$ {dados['descontos']:.2f}")
                        st.write(f"**Valor Final Pago:** R$ {dados['valor_final_pago']:.2f}")

                        if st.button("Confirmar e Salvar"):
                            st.session_state["compra_confirmada"] = True
                            st.session_state["dados_finais"] = {
                                "Nome Mercado": [dados["nome_mercado"]],
                                "Cidade": [dados["cidade"]],
                                "Data Compra": [data_compra_str],
                                "Valor Total": [dados["valor_total"]],
                                "Descontos": [dados["descontos"]],
                                "Valor Final Pago": [dados["valor_final_pago"]]
                            }
                            # Salvar dados para envio ao Supabase
                            st.session_state["itens_supabase"] = itens_supabase
                            st.session_state["dados_compra"] = {
                                "nome_mercado": dados["nome_mercado"],
                                "cidade": dados["cidade"],
                                "data_compra": data_compra_str,
                                "valor_total": dados["valor_total"],
                                "descontos": dados["descontos"],
                                "valor_final_pago": dados["valor_final_pago"]
                            }
                            st.session_state.pop("dados_para_confirmar")
                            st.rerun()

                    # Exibe o resultado final se confirmado
                    if st.session_state.get("compra_confirmada", False):
                        df_finais = pd.DataFrame(st.session_state["dados_finais"])
                        st.success("Informações adicionadas com sucesso!")
                        st.subheader("Resultado Compra")
                        st.dataframe(df_finais)
                        
                        # Botão para registrar a compra
                        if st.button("Registrar Compra"):
                            # Verificar se temos os dados necessários
                            if (st.session_state.get("itens_supabase") and 
                                st.session_state.get("dados_compra")):
                                
                                itens_supabase = st.session_state["itens_supabase"]
                                dados_compra = st.session_state["dados_compra"]
                                
                                # Contador para acompanhar o progresso
                                total_itens = len(itens_supabase)
                                itens_registrados = 0
                                
                                # Barra de progresso
                                progress_bar = st.progress(0)
                                status_text = st.empty()
                                
                                # Registrar cada item no Supabase
                                for i, item in enumerate(itens_supabase):
                                    status_text.text(f"Registrando item {i+1} de {total_itens}: {item['descricao']}")
                                    
                                    result = create_supabase_page(item, dados_compra)
                                    if result:
                                        itens_registrados += 1
                                    
                                    # Atualizar barra de progresso
                                    progress = (i + 1) / total_itens
                                    progress_bar.progress(progress)
                                
                                # Limpar barra de progresso
                                progress_bar.empty()
                                status_text.empty()
                                
                                if itens_registrados == total_itens:
                                    st.success(f"✅ Compra Registrada Com Sucesso! {itens_registrados} itens foram salvos no Supabase.")
                                else:
                                    st.warning(f"⚠️ {itens_registrados} de {total_itens} itens foram registrados. Verifique os erros acima.")
                            else:
                                st.error("❌ Dados da compra não encontrados. Tente novamente.")
                else:
                    st.warning("Não foi possível identificar os itens da compra automaticamente. Verifique se o PDF segue o padrão esperado.")
            except Exception as e:
                st.error(f"Erro ao tentar ler o PDF: {e}")
        else:
            st.info("Aguardando o upload de um arquivo PDF...")
    
    # Modo Registro Manual
    if st.session_state.modo_registro == "manual":
        st.write("Insira os dados da compra manualmente:")
        
        # Formulário para informações da compra
        with st.form("form_compra_manual"):
            st.subheader("📋 Informações da Compra")
            col1, col2 = st.columns(2)
            
            with col1:
                nome_mercado = st.text_input("Nome do Mercado", key="manual_mercado")
                data_compra = st.date_input("Data da Compra", value=datetime.date.today(), key="manual_data")
            
            with col2:
                cidade = st.text_input("Cidade", key="manual_cidade")
                valor_total = st.number_input("Valor Total", value=0.0, format="%.2f", key="manual_valor_total")
            
            descontos = st.number_input("Descontos", value=0.0, format="%.2f", key="manual_descontos")
            valor_final_pago = valor_total - descontos
            
            st.write(f"**Valor Final Pago:** R$ {valor_final_pago:.2f}")
            
            # Seção para adicionar itens
            st.subheader("📦 Itens da Compra")
            
            # Inicializar lista de itens se não existir
            if "itens_manuais" not in st.session_state:
                st.session_state.itens_manuais = []
            
            # Formulário para adicionar item
            with st.expander("➕ Adicionar Novo Item", expanded=True):
                col1, col2 = st.columns(2)
                
                with col1:
                    codigo = st.text_input("Código", key="manual_codigo")
                    descricao = st.text_input("Descrição", key="manual_descricao")
                    quantidade = st.number_input("Quantidade", value=1.0, format="%.2f", key="manual_quantidade")
                
                with col2:
                    unidade = st.text_input("Unidade", value="UN", key="manual_unidade")
                    valor_unitario = st.number_input("Valor Unitário", value=0.0, format="%.2f", key="manual_valor_unit")
                
                valor_total_item = quantidade * valor_unitario
                st.write(f"**Valor Total do Item:** R$ {valor_total_item:.2f}")
                
                if st.form_submit_button("➕ Adicionar Item"):
                    if codigo and descricao and quantidade > 0 and valor_unitario > 0:
                        novo_item = {
                            "item": len(st.session_state.itens_manuais) + 1,
                            "codigo": codigo,
                            "descricao": descricao,
                            "quantidade": quantidade,
                            "unidade": unidade,
                            "valor_unitario": valor_unitario,
                            "valor_total": valor_total_item
                        }
                        st.session_state.itens_manuais.append(novo_item)
                        st.success(f"Item '{descricao}' adicionado com sucesso!")
                        st.rerun()
                    else:
                        st.error("Por favor, preencha todos os campos obrigatórios.")
            
            # Exibir itens adicionados
            if st.session_state.itens_manuais:
                st.subheader("📋 Itens Adicionados")
                
                # Criar DataFrame para exibição
                itens_display = []
                for item in st.session_state.itens_manuais:
                    itens_display.append([
                        item["item"],
                        item["codigo"],
                        item["descricao"],
                        item["quantidade"],
                        item["unidade"],
                        item["valor_unitario"],
                        item["valor_total"]
                    ])
                
                df_itens_manuais = pd.DataFrame(itens_display, columns=colunas_itens)
                st.dataframe(df_itens_manuais)
                
                # Botão para remover último item
                if st.button("🗑️ Remover Último Item"):
                    if st.session_state.itens_manuais:
                        item_removido = st.session_state.itens_manuais.pop()
                        st.success(f"Item '{item_removido['descricao']}' removido!")
                        st.rerun()
                
                # Botão para limpar todos os itens
                if st.button("🗑️ Limpar Todos os Itens"):
                    st.session_state.itens_manuais = []
                    st.success("Todos os itens foram removidos!")
                    st.rerun()
            
            # Botão para confirmar compra
            if st.form_submit_button("✅ Confirmar Compra"):
                if (nome_mercado and cidade and st.session_state.itens_manuais):
                    # Salvar dados para confirmação
                    st.session_state["dados_para_confirmar"] = {
                        "nome_mercado": nome_mercado,
                        "cidade": cidade,
                        "data_compra": data_compra,
                        "valor_total": valor_total,
                        "descontos": descontos,
                        "valor_final_pago": valor_final_pago
                    }
                    st.session_state["itens_supabase"] = st.session_state.itens_manuais
                    st.session_state["compra_confirmada"] = True
                    st.rerun()
                else:
                    st.error("Por favor, preencha todas as informações obrigatórias e adicione pelo menos um item.")
        
        # Exibir confirmação se houver dados
        if st.session_state.get("compra_confirmada", False) and st.session_state.get("dados_para_confirmar"):
            dados = st.session_state["dados_para_confirmar"]
            data_compra_str = dados["data_compra"].strftime('%d/%m/%Y')
            
            st.success("✅ Compra confirmada! Dados para registro:")
            st.write(f"**Nome Mercado:** {dados['nome_mercado']}")
            st.write(f"**Cidade:** {dados['cidade']}")
            st.write(f"**Data Compra:** {data_compra_str}")
            st.write(f"**Valor Total:** R$ {dados['valor_total']:.2f}")
            st.write(f"**Descontos:** R$ {dados['descontos']:.2f}")
            st.write(f"**Valor Final Pago:** R$ {dados['valor_final_pago']:.2f}")
            st.write(f"**Total de Itens:** {len(st.session_state.itens_manuais)}")
            
            # Botão para registrar no Supabase
            if st.button("💾 Registrar no Supabase"):
                if (st.session_state.get("itens_supabase") and 
                    st.session_state.get("dados_para_confirmar")):
                    
                    itens_supabase = st.session_state["itens_supabase"]
                    dados_compra = {
                        "nome_mercado": dados["nome_mercado"],
                        "cidade": dados["cidade"],
                        "data_compra": data_compra_str,
                        "valor_total": dados["valor_total"],
                        "descontos": dados["descontos"],
                        "valor_final_pago": dados["valor_final_pago"]
                    }
                    
                    # Contador para acompanhar o progresso
                    total_itens = len(itens_supabase)
                    itens_registrados = 0
                    
                    # Barra de progresso
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    # Registrar cada item no Supabase
                    for i, item in enumerate(itens_supabase):
                        status_text.text(f"Registrando item {i+1} de {total_itens}: {item['descricao']}")
                        
                        result = create_supabase_page(item, dados_compra)
                        if result:
                            itens_registrados += 1
                        
                        # Atualizar barra de progresso
                        progress = (i + 1) / total_itens
                        progress_bar.progress(progress)
                    
                    # Limpar barra de progresso
                    progress_bar.empty()
                    status_text.empty()
                    
                    if itens_registrados == total_itens:
                        st.success(f"✅ Compra Registrada Com Sucesso! {itens_registrados} itens foram salvos no Supabase.")
                        # Limpar dados da sessão
                        st.session_state.pop("itens_manuais", None)
                        st.session_state.pop("compra_confirmada", None)
                        st.session_state.pop("dados_para_confirmar", None)
                        st.session_state.pop("itens_supabase", None)
                    else:
                        st.warning(f"⚠️ {itens_registrados} de {total_itens} itens foram registrados. Verifique os erros acima.")
                else:
                    st.error("❌ Dados da compra não encontrados. Tente novamente.")