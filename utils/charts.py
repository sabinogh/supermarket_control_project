import plotly.express as px
import pandas as pd

def plot_gastos_por_dia(compras):
    """
    Gera um gráfico de linha mostrando os gastos por dia
    com base na lista de compras vinda do banco.
    """
    if not compras or len(compras) == 0:
        return px.line(pd.DataFrame(), x=[], y=[])

    df = pd.DataFrame(compras)

    # Garante que a coluna data esteja em formato datetime
    if "data_compra" in df.columns:
        df["data_compra"] = pd.to_datetime(df["data_compra"])

    # Cria gráfico
    fig = px.line(
        df,
        x="data_compra",
        y="valor_final_pago",
        markers=True,
        title="📊 Gastos por Dia"
    )
    fig.update_layout(xaxis_title="Data da Compra", yaxis_title="Valor Pago (R$)")
    return fig
