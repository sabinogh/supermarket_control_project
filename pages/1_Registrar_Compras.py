import streamlit as st
from services import db_queries
import pandas as pd
import pdfplumber
import re

st.title("📝 Registrar Compras")
st.write("Aqui você pode registrar via upload de nota fiscal (PDF) ou manualmente.")

modo = st.radio("Escolha o modo de registro:", ["Upload PDF", "Manual"])

if modo == "Upload PDF":
    colunas_itens = ["Item", "Código", "Descrição", "Quantidade", "Unidade", "Valor Unitário", "Valor Total"]

    uploaded_file = st.file_uploader("Faça upload da sua nota fiscal (PDF)", type=["pdf"])
    if uploaded_file is not None:
        st.success(f"Arquivo '{uploaded_file.name}' enviado com sucesso!")
        try:
            with pdfplumber.open(uploaded_file) as pdf:
                texto = ""
                for page in pdf.pages:
                    texto += page.extract_text() + "\n"

            # Regex para extrair os itens do PDF
            padrao_item = re.compile(
                r"(.+?) \(Código: (\d+) \) Vl\. Total\s*\nQtde\.:([\d,.]+) UN: (\w+) Vl\. Unit\.: ([\d,.]+) ([\d,.]+)"
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
                    st.info("Nenhum mercado cadastrado. Volte e cadastre um mercado antes de registrar a compra.")
                else:
                    opcoes = [f"{m['nome']} - {m['cidade']}" for m in mercados]
                    idx = st.selectbox("Mercado", options=list(range(len(opcoes))),
                                       format_func=lambda i: opcoes[i], key="select_mercado")
                    mercado_selecionado = mercados[idx]

                    # Informações adicionais
                    desconto = st.number_input("Descontos aplicados (R$)", min_value=0.0,
                                               max_value=float(valor_total_lido), value=0.0, step=0.01,
                                               key="desconto_compra")
                    data_compra = st.date_input("Data da compra", key="data_compra")

                    valor_final_pago = valor_total_lido - desconto

                    if st.button("Registrar Compra no Banco de Dados"):
                        try:
                            # 1. Inserir cabeçalho
                            compra = db_queries.insert_compra({
                                "mercado_id": mercado_selecionado["id"],
                                "data_compra": data_compra,
                                "valor_total": valor_total_lido,
                                "descontos": desconto,
                                "valor_final_pago": valor_final_pago
                            })

                            if not compra:
                                st.error("Erro ao registrar cabeçalho da compra.")
                            else:
                                compra_id = compra["id"]

                                # 2. Inserir itens
                                total_itens = len(itens_supabase)
                                itens_registrados = 0
                                progress_bar = st.progress(0)
                                status_text = st.empty()

                                for i, item in enumerate(itens_supabase):
                                    status_text.text(f"Registrando item {i+1} de {total_itens}: {item['descricao']}")
                                    try:
                                        db_queries.insert_item({
                                            "compra_id": compra_id,
                                            **item
                                        })
                                        itens_registrados += 1
                                    except Exception as e:
                                        st.warning(f"Erro ao registrar item: {item['descricao']} - {e}")

                                    progress = (i + 1) / total_itens
                                    progress_bar.progress(progress)

                                progress_bar.empty()
                                status_text.empty()

                                if itens_registrados == total_itens:
                                    st.success(f"✅ Compra registrada com sucesso! {itens_registrados} itens salvos.")
                                else:
                                    st.warning(f"⚠️ {itens_registrados} de {total_itens} itens foram registrados.")

                        except Exception as e:
                            st.error(f"Erro ao registrar compra: {e}")

            else:
                st.warning("Não foi possível identificar os itens da compra automaticamente. Verifique se o PDF segue o padrão esperado.")

        except Exception as e:
            st.error(f"Erro ao tentar ler o PDF: {e}")
    else:
        st.info("Aguardando o upload de um arquivo PDF...")
