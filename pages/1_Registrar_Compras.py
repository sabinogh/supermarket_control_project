import streamlit as st
from services import db_queries
import pandas as pd
import pdfplumber
import re
import datetime

st.sidebar.title("Menu de Navegação")
st.sidebar.markdown("""GSproject""")

st.title("📝 Registrar Compras")
st.write("Aqui você pode registrar via upload de nota fiscal (PDF) ou manualmente.")

modo = st.radio("Escolha o modo de registro:", ["Upload PDF", "Manual"])

# Função para registrar a compra e seus itens
def registrar_compra_e_itens(mercado_id, data_compra, valor_total_cabecalho, descontos_cabecalho, valor_final_pago_cabecalho, itens_para_db):
    try:
        # 1. Inserir cabeçalho da compra
        compra_cabecalho_data = {
            "mercado_id": mercado_id,
            "data_compra": data_compra,
            "valor_total": valor_total_cabecalho,
            "descontos": descontos_cabecalho,
            "valor_final_pago": valor_final_pago_cabecalho
        }
        compra_registrada = db_queries.insert_compra(compra_cabecalho_data)

        if not compra_registrada:
            st.error("Erro ao registrar cabeçalho da compra.")
            return False

        compra_id = compra_registrada["id"]

        # 2. Inserir itens da compra
        total_itens = len(itens_para_db)
        itens_registrados = 0
        progress_bar = st.progress(0)
        status_text = st.empty()

        for i, item in enumerate(itens_para_db):
            status_text.text(f"Registrando item {i+1} de {total_itens}: {item["descricao"]}")
            try:
                db_queries.insert_item({
                    "compra_id": compra_id,
                    **item
                })
                itens_registrados += 1
            except Exception as e:
                st.warning(f"Erro ao registrar item: {item["descricao"]} - {e}")

            progress = (i + 1) / total_itens
            progress_bar.progress(progress)

        progress_bar.empty()
        status_text.empty()

        if itens_registrados == total_itens:
            st.success(f"✅ Compra registrada com sucesso! {itens_registrados} itens salvos.")
            return True
        else:
            st.warning(f"⚠️ {itens_registrados} de {total_itens} itens foram registrados.")
            return False

    except Exception as e:
        st.error(f"Erro geral ao registrar compra: {e}")
        return False


if modo == "Upload PDF":
    colunas_itens = ["Item", "Código", "Descrição", "Quantidade", "Unidade", "Valor Unitário", "Valor Total"]

    uploaded_file = st.file_uploader("Faça upload da sua nota fiscal (PDF)", type=["pdf"])
    if uploaded_file is not None:
        st.success(f"Arquivo \'{uploaded_file.name}\' enviado com sucesso!")
        try:
            with pdfplumber.open(uploaded_file) as pdf:
                texto = ""
                for page in pdf.pages:
                    texto += page.extract_text() + "\n"

            # Regex para extrair os itens do PDF
            # Padrão ajustado para capturar: Descrição, Código, Quantidade, Unidade, Valor Unitário, Valor Total
            # Tornando a regex mais robusta a variações de espaçamento e garantindo a captura correta dos grupos.
            # Removido \\ de \\( e \\) pois não são necessários para escapar parênteses literais em Python regex strings.
            padrao_item = re.compile(
                r"(.+?) \(Código:\s*(\d+)\s*\) Vl\.\s*Total\s*\nQtde\.:([\d,.]+) UN:\s*(\w+)\s*Vl\.\s*Unit\.:\s*([\d,.]+) ([\d,.]+)"
            )

            itens_tabela = []
            itens_supabase = []
            for i, match in enumerate(padrao_item.finditer(texto), 1):
                descricao = match.group(1).strip()
                codigo = match.group(2).strip()
                quantidade = match.group(3).replace(",", ".")
                unidade = match.group(4).strip()
                valor_unit = match.group(5).replace(",", ".")
                valor_total = match.group(6).replace(",", ".")

                itens_tabela.append([
                    i, codigo, descricao, float(quantidade), unidade,
                    float(valor_unit), float(valor_total)
                ])

                itens_supabase.append({
                    "codigo": codigo,
                    "descricao": descricao,
                    "quantidade": float(quantidade),
                    "unidade": unidade,
                    "valor_unitario": float(valor_unit),
                    "valor_total": float(valor_total)
                })

            if itens_tabela:
                df_itens = pd.DataFrame(itens_tabela, columns=colunas_itens)
                st.subheader("📦 Itens da Compra (extraído do PDF)")
                st.dataframe(df_itens)

                valor_total_lido = df_itens["Valor Total"].sum()

                # Seleção do mercado
                mercados = db_queries.buscar_mercados()
                st.subheader("Selecione o Mercado")
                if not mercados:
                    st.info("Nenhum mercado cadastrado. Por favor, vá para a página \'Mercados\' e cadastre um mercado antes de registrar a compra.")
                else:
                    opcoes = [f"{m['nome']} - {m['cidade']}" for m in mercados]
                    idx = st.selectbox("Mercado", options=list(range(len(opcoes))),
                                       format_func=lambda i: opcoes[i], key="select_mercado_pdf")
                    mercado_selecionado = mercados[idx]

                    # Informações adicionais
                    desconto = st.number_input("Descontos aplicados (R$)", min_value=0.0,
                                               max_value=float(valor_total_lido), value=0.0, step=0.01,
                                               key="desconto_compra_pdf")
                    data_compra = st.date_input("Data da compra", key="data_compra_pdf")

                    valor_final_pago = valor_total_lido - desconto

                    if st.button("Registrar Compra no Banco de Dados (PDF)"):
                        registrar_compra_e_itens(mercado_selecionado["id"], data_compra, valor_total_lido, desconto, valor_final_pago, itens_supabase)

            else:
                st.warning("Não foi possível identificar os itens da compra automaticamente. Verifique se o PDF segue o padrão esperado.")

        except Exception as e:
            st.error(f"Erro ao tentar ler o PDF: {e}")
    else:
        st.info("Aguardando o upload de um arquivo PDF...")

elif modo == "Manual":
    st.subheader("✍️ Registro Manual de Compra")

    # Seleção do mercado
    mercados = db_queries.buscar_mercados()
    if not mercados:
        st.info("Nenhum mercado cadastrado. Por favor, vá para a página \'Mercados\' e cadastre um mercado antes de registrar a compra.")
    else:
        opcoes_mercados = [f"{m['nome']} - {m['cidade']}" for m in mercados]
        idx_mercado_manual = st.selectbox("Selecione o Mercado", options=list(range(len(opcoes_mercados))),
                                           format_func=lambda i: opcoes_mercados[i], key="select_mercado_manual")
        mercado_selecionado_manual = mercados[idx_mercado_manual]

        data_compra_manual = st.date_input("Data da Compra", value=datetime.date.today(), key="data_compra_manual")
        descontos_manual = st.number_input("Descontos Aplicados (R$)", min_value=0.0, value=0.0, step=0.01, key="descontos_manual")

        st.markdown("--- ")
        st.subheader("Adicionar Itens da Compra")

        # Inicializa a lista de itens na sessão do Streamlit
        if 'itens_manuais' not in st.session_state:
            st.session_state.itens_manuais = []

        # Formulário para adicionar um novo item
        with st.form(key='add_item_form', clear_on_submit=True):
            col_desc, col_qtd, col_un, col_vu = st.columns([3, 1, 1, 1.5])
            with col_desc:
                descricao_item = st.text_input("Descrição do Item", key="desc_item")
            with col_qtd:
                quantidade_item = st.number_input("Quantidade", min_value=0.01, value=1.0, step=0.01, key="qtd_item")
            with col_un:
                unidade_item = st.selectbox("Unidade", options=["UN", "KG", "LT"], key="un_item")
            with col_vu:
                valor_unitario_item = st.number_input("Valor Unitário (R$)", min_value=0.01, value=0.01, step=0.01, key="vu_item")
            
            # Calcula o valor total do item
            valor_total_item = quantidade_item * valor_unitario_item
            st.write(f"Valor Total do Item: R$ {valor_total_item:.2f}")

            add_item_button = st.form_submit_button("➕ Adicionar Item")

            if add_item_button:
                if descricao_item and unidade_item and quantidade_item > 0 and valor_unitario_item > 0:
                    st.session_state.itens_manuais.append({
                        "codigo": "MANUAL", # Código padrão para itens manuais
                        "descricao": descricao_item,
                        "quantidade": quantidade_item,
                        "unidade": unidade_item,
                        "valor_unitario": valor_unitario_item,
                        "valor_total": valor_total_item
                    })
                    st.success("Item adicionado!")
                else:
                    st.warning("Por favor, preencha todos os campos do item corretamente.")

        # Exibe os itens adicionados em uma tabela
        if st.session_state.itens_manuais:
            st.subheader("Itens Adicionados")
            df_itens_manuais = pd.DataFrame(st.session_state.itens_manuais)
            df_itens_manuais_display = df_itens_manuais.rename(columns={
                "codigo": "Código",
                "descricao": "Descrição",
                "quantidade": "Quantidade",
                "unidade": "Unidade",
                "valor_unitario": "Valor Unitário",
                "valor_total": "Valor Total"
            })
            st.dataframe(df_itens_manuais_display, use_container_width=True)

            # Calcula o valor total da compra manual
            valor_total_compra_manual = df_itens_manuais["valor_total"].sum()
            st.markdown(f"**Valor Total dos Itens: R$ {valor_total_compra_manual:.2f}**")

            valor_final_pago_manual = valor_total_compra_manual - descontos_manual
            st.markdown(f"**Valor Final da Compra (com descontos): R$ {valor_final_pago_manual:.2f}**")

            if st.button("Registrar Compra Manual no Banco de Dados"):
                if st.session_state.itens_manuais:
                    registrar_compra_e_itens(
                        mercado_selecionado_manual["id"],
                        data_compra_manual,
                        valor_total_compra_manual,
                        descontos_manual,
                        valor_final_pago_manual,
                        st.session_state.itens_manuais
                    )
                    # Limpa os itens da sessão após o registro
                    st.session_state.itens_manuais = []
                    st.experimental_rerun()
                else:
                    st.warning("Adicione ao menos um item para registrar a compra.")
        else:
            st.info("Nenhum item adicionado ainda.")


