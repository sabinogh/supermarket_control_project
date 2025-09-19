"""
Script de teste para verificar o sistema de autenticação
Este script testa as principais funcionalidades do sistema de login
"""

import os
import sys
from dotenv import load_dotenv

# Carrega variáveis do arquivo .env
load_dotenv()

def test_supabase_connection():
    """Testa a conexão com o Supabase"""
    print("🔧 Testando conexão com Supabase...")
    
    try:
        from services.supabase_client import supabase
        # Testa uma query simples
        response = supabase.table("mercados").select("count", count="exact").execute()
        print(f"✅ Conexão com Supabase OK - {response.count} mercados encontrados")
        return True
    except Exception as e:
        print(f"❌ Erro na conexão com Supabase: {e}")
        return False

def test_auth_functions():
    """Testa as funções de autenticação"""
    print("🔧 Testando funções de autenticação...")
    
    try:
        from services.supabase_client import (
            get_current_user,
            is_user_authenticated,
            get_user_id,
            get_user_email,
            is_admin_user
        )
        
        print("✅ Todas as funções de autenticação importadas com sucesso")
        
        # Testa funções sem usuário logado
        user = get_current_user()
        authenticated = is_user_authenticated()
        user_id = get_user_id()
        user_email = get_user_email()
        is_admin = is_admin_user()
        
        print(f"📊 Estado atual:")
        print(f"   - Usuário: {user}")
        print(f"   - Autenticado: {authenticated}")
        print(f"   - User ID: {user_id}")
        print(f"   - Email: {user_email}")
        print(f"   - Admin: {is_admin}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao testar funções de autenticação: {e}")
        return False

def test_database_structure():
    """Testa a estrutura do banco de dados"""
    print("🔧 Testando estrutura do banco de dados...")
    
    tables_to_test = ["mercados", "compras_itens"]
    
    try:
        from services.supabase_client import supabase
        
        for table in tables_to_test:
            try:
                response = supabase.table(table).select("*").limit(1).execute()
                print(f"✅ Tabela '{table}' acessível - {len(response.data)} registros encontrados")
            except Exception as e:
                print(f"❌ Erro ao acessar tabela '{table}': {e}")
                return False
        
        return True
    except Exception as e:
        print(f"❌ Erro ao importar supabase: {e}")
        return False

def test_environment_variables():
    """Testa as variáveis de ambiente"""
    print("🔧 Testando variáveis de ambiente...")
    
    required_vars = ["SUPABASE_URL", "SUPABASE_KEY"]
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {'*' * 10}...{value[-10:]}")
        else:
            print(f"❌ {var}: Não encontrada")
            return False
    
    # Testa ADMIN_EMAILS (opcional)
    admin_emails = os.getenv("ADMIN_EMAILS", "")
    if admin_emails:
        print(f"✅ ADMIN_EMAILS: {admin_emails}")
    else:
        print("⚠️ ADMIN_EMAILS: Não configurada (opcional)")
    
    return True

def test_file_structure():
    """Testa a estrutura de arquivos"""
    print("🔧 Testando estrutura de arquivos...")
    
    required_files = [
        "0_Página_Inicial.py",
        "pages/Login.py",
        "pages/1_Registrar_Compras.py",
        "pages/2_Analisar_Compras.py",
        "pages/3_Mercados.py",
        "pages/4_Dashboard_Analise.py",
        "services/supabase_client.py",
        "services/db_queries.py",
        "requirements.txt"
    ]
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}: Não encontrado")
            return False
    
    return True

def run_all_tests():
    """Executa todos os testes"""
    print("🚀 Iniciando testes do sistema de autenticação...")
    print("=" * 60)
    
    tests = [
        ("Variáveis de Ambiente", test_environment_variables),
        ("Estrutura de Arquivos", test_file_structure),
        ("Conexão Supabase", test_supabase_connection),
        ("Estrutura do Banco", test_database_structure),
        ("Funções de Autenticação", test_auth_functions)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 40)
        result = test_func()
        results.append((test_name, result))
        print()
    
    print("=" * 60)
    print("📊 RESUMO DOS TESTES")
    print("=" * 60)
    
    all_passed = True
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    print()
    if all_passed:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("✅ O sistema de autenticação está pronto para uso.")
        print()
        print("🔔 PRÓXIMOS PASSOS:")
        print("1. Execute: streamlit run 0_Página_Inicial.py")
        print("2. Teste o registro de um novo usuário")
        print("3. Teste o login com o usuário criado")
        print("4. Verifique se as páginas requerem autenticação")
        print("5. Teste o isolamento de dados entre usuários")
    else:
        print("⚠️ ALGUNS TESTES FALHARAM!")
        print("❌ Corrija os problemas antes de usar o sistema.")
    
    return all_passed

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

