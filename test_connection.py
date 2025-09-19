from supabase import create_client

SUPABASE_URL = "https://wufmrqnmzcykiytqynhv.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind1Zm1ycW5temN5a2l5dHF5bmh2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTUyNTk2NzUsImV4cCI6MjA3MDgzNTY3NX0.lx44jf873UGPZZnCruSbEMLnnn8ya8N3dsXji_8w3YA"

try:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    response = supabase.table("compras_itens").select("*").limit(1).execute()
    print("Conexão bem-sucedida!")
    print(response.data)
except Exception as e:
    print("Erro ao conectar no Supabase:")
    print(e)


