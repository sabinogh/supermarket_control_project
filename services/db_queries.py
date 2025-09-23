from services.supabase_client import supabase

# ======================
# MERCADOS
# ======================

def registrar_mercado(nome, cidade):
    """Insere um novo mercado no banco"""
    data = {"nome": nome, "cidade": cidade}
    res = supabase.table("mercados").insert(data).execute()
    return res.data

def buscar_mercados():
    """Busca todos os mercados cadastrados"""
    res = supabase.table("mercados").select("*").order("nome", desc=False).execute()
    return res.data

# ======================
# COMPRAS (CABEÇALHO)
# ======================

def insert_compra(data):
    """
    Insere o cabeçalho de uma compra e retorna o registro criado.
    Espera um dicionário no formato:
    {
        "mercado_id": int,
        "data_compra": "YYYY-MM-DD",
        "valor_total": float,
        "descontos": float,
        "valor_final_pago": float
    }
    """
    res = supabase.table("compras_cabecalho").insert(data).execute()
    return res.data[0] if res.data else None

def get_compras_cabecalho_periodo(start_date, end_date):
    """Busca compras em um intervalo de datas (apenas cabeçalho)"""
    res = (
        supabase.table("compras_cabecalho")
        .select("*")
        .gte("data_compra", str(start_date))
        .lte("data_compra", str(end_date))
        .order("data_compra", desc=False)
        .execute()
    )
    return res.data

def get_compras_detalhadas_rpc(start_date, end_date):
    """Chama a função RPC para buscar compras detalhadas em um intervalo de datas"""
    res = supabase.rpc(
        "get_compras_detalhadas_periodo",
        {"data_inicio": str(start_date), "data_fim": str(end_date)}
    ).execute()
    return res.data

# ======================
# ITENS DA COMPRA
# ======================

def insert_item(data):
    """
    Insere um item vinculado a uma compra.
    Espera um dicionário no formato:
    {
        "compra_id": int,
        "user_id": str,  # Necessário para RLS
        "codigo": str,
        "descricao": str,
        "quantidade": float,
        "unidade": str,
        "valor_unitario": float,
        "valor_total": float
    }
    """
    res = supabase.table("compras_itens").insert(data).execute()
    return res.data

def get_itens_por_compra(compra_id):
    """Busca todos os itens de uma compra específica"""
    res = supabase.table("compras_itens").select("*").eq("compra_id", compra_id).execute()
    return res.data
