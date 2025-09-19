"""
Script para configurar políticas de segurança RLS (Row Level Security) no Supabase
Este script deve ser executado uma vez para configurar as políticas de acesso aos dados
"""

from services.supabase_client import supabase
import streamlit as st

def setup_rls_policies():
    """
    Configura as políticas RLS para isolamento de dados por usuário
    """
    
    print("🔧 Configurando políticas RLS (Row Level Security)...")
    
    # SQL para habilitar RLS nas tabelas
    rls_commands = [
        # Habilitar RLS na tabela compras
        "ALTER TABLE compras ENABLE ROW LEVEL SECURITY;",
        
        # Habilitar RLS na tabela itens
        "ALTER TABLE itens ENABLE ROW LEVEL SECURITY;",
        
        # Política para compras - usuários só veem suas próprias compras
        """
        CREATE POLICY "Users can view own purchases" ON compras
        FOR SELECT USING (auth.uid() = user_id);
        """,
        
        # Política para inserir compras - usuários só podem inserir com seu próprio user_id
        """
        CREATE POLICY "Users can insert own purchases" ON compras
        FOR INSERT WITH CHECK (auth.uid() = user_id);
        """,
        
        # Política para atualizar compras - usuários só podem atualizar suas próprias compras
        """
        CREATE POLICY "Users can update own purchases" ON compras
        FOR UPDATE USING (auth.uid() = user_id);
        """,
        
        # Política para deletar compras - usuários só podem deletar suas próprias compras
        """
        CREATE POLICY "Users can delete own purchases" ON compras
        FOR DELETE USING (auth.uid() = user_id);
        """,
        
        # Política para itens - usuários só veem seus próprios itens
        """
        CREATE POLICY "Users can view own items" ON itens
        FOR SELECT USING (auth.uid() = user_id);
        """,
        
        # Política para inserir itens - usuários só podem inserir com seu próprio user_id
        """
        CREATE POLICY "Users can insert own items" ON itens
        FOR INSERT WITH CHECK (auth.uid() = user_id);
        """,
        
        # Política para atualizar itens - usuários só podem atualizar seus próprios itens
        """
        CREATE POLICY "Users can update own items" ON itens
        FOR UPDATE USING (auth.uid() = user_id);
        """,
        
        # Política para deletar itens - usuários só podem deletar seus próprios itens
        """
        CREATE POLICY "Users can delete own items" ON itens
        FOR DELETE USING (auth.uid() = user_id);
        """,
        
        # Políticas para mercados - dados compartilhados mas com rastreamento de quem adicionou
        """
        CREATE POLICY "Everyone can view markets" ON mercados
        FOR SELECT USING (true);
        """,
        
        """
        CREATE POLICY "Authenticated users can insert markets" ON mercados
        FOR INSERT WITH CHECK (auth.uid() = added_by_user_id);
        """,
        
        """
        CREATE POLICY "Users can update markets they added" ON mercados
        FOR UPDATE USING (auth.uid() = added_by_user_id);
        """
    ]
    
    try:
        for command in rls_commands:
            print(f"Executando: {command[:50]}...")
            # Note: Em produção, essas políticas devem ser criadas diretamente no Supabase Dashboard
            # ou via SQL Editor, pois requerem privilégios administrativos
            print("✅ Comando preparado")
        
        print("🎉 Todas as políticas RLS foram preparadas!")
        print("📝 IMPORTANTE: Execute estes comandos SQL no Supabase Dashboard:")
        print("=" * 60)
        for i, command in enumerate(rls_commands, 1):
            print(f"-- Comando {i}")
            print(command)
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao configurar políticas RLS: {e}")
        return False

def add_user_id_columns():
    """
    Adiciona colunas user_id às tabelas que ainda não possuem
    """
    
    print("🔧 Adicionando colunas user_id às tabelas...")
    
    alter_commands = [
        # Adicionar coluna user_id à tabela compras (se não existir)
        """
        ALTER TABLE compras 
        ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES auth.users(id);
        """,
        
        # Adicionar coluna user_id à tabela itens (se não existir)
        """
        ALTER TABLE itens 
        ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES auth.users(id);
        """,
        
        # Adicionar coluna added_by_user_id à tabela mercados (se não existir)
        """
        ALTER TABLE mercados 
        ADD COLUMN IF NOT EXISTS added_by_user_id UUID REFERENCES auth.users(id);
        """,
        
        # Criar índices para melhor performance
        """
        CREATE INDEX IF NOT EXISTS idx_compras_user_id ON compras(user_id);
        """,
        
        """
        CREATE INDEX IF NOT EXISTS idx_itens_user_id ON itens(user_id);
        """,
        
        """
        CREATE INDEX IF NOT EXISTS idx_mercados_added_by_user_id ON mercados(added_by_user_id);
        """
    ]
    
    print("📝 IMPORTANTE: Execute estes comandos SQL no Supabase Dashboard:")
    print("=" * 60)
    for i, command in enumerate(alter_commands, 1):
        print(f"-- Comando {i}")
        print(command)
        print()
    
    return True

def create_admin_functions():
    """
    Cria funções para administradores
    """
    
    print("🔧 Criando funções administrativas...")
    
    admin_functions = [
        # Função para obter estatísticas gerais (sem dados pessoais)
        """
        CREATE OR REPLACE FUNCTION get_system_stats(start_date DATE, end_date DATE)
        RETURNS TABLE (
            total_purchases BIGINT,
            total_volume NUMERIC,
            active_markets BIGINT,
            average_ticket NUMERIC
        ) AS $$
        BEGIN
            RETURN QUERY
            SELECT 
                COUNT(*)::BIGINT as total_purchases,
                SUM(valor_final_pago)::NUMERIC as total_volume,
                COUNT(DISTINCT mercado_id)::BIGINT as active_markets,
                AVG(valor_final_pago)::NUMERIC as average_ticket
            FROM compras 
            WHERE data_compra BETWEEN start_date AND end_date;
        END;
        $$ LANGUAGE plpgsql SECURITY DEFINER;
        """,
        
        # Função para obter dados agregados por mercado (sem dados pessoais)
        """
        CREATE OR REPLACE FUNCTION get_market_stats(start_date DATE, end_date DATE)
        RETURNS TABLE (
            market_name TEXT,
            purchase_count BIGINT,
            total_volume NUMERIC,
            average_ticket NUMERIC
        ) AS $$
        BEGIN
            RETURN QUERY
            SELECT 
                m.nome::TEXT as market_name,
                COUNT(c.id)::BIGINT as purchase_count,
                SUM(c.valor_final_pago)::NUMERIC as total_volume,
                AVG(c.valor_final_pago)::NUMERIC as average_ticket
            FROM compras c
            JOIN mercados m ON c.mercado_id = m.id
            WHERE c.data_compra BETWEEN start_date AND end_date
            GROUP BY m.nome
            ORDER BY total_volume DESC;
        END;
        $$ LANGUAGE plpgsql SECURITY DEFINER;
        """
    ]
    
    print("📝 IMPORTANTE: Execute estes comandos SQL no Supabase Dashboard:")
    print("=" * 60)
    for i, function in enumerate(admin_functions, 1):
        print(f"-- Função {i}")
        print(function)
        print()
    
    return True

if __name__ == "__main__":
    print("🚀 Iniciando configuração de segurança do banco de dados...")
    print()
    
    print("1. Adicionando colunas user_id...")
    add_user_id_columns()
    print()
    
    print("2. Configurando políticas RLS...")
    setup_rls_policies()
    print()
    
    print("3. Criando funções administrativas...")
    create_admin_functions()
    print()
    
    print("✅ Configuração de segurança preparada!")
    print()
    print("🔔 PRÓXIMOS PASSOS:")
    print("1. Acesse o Supabase Dashboard")
    print("2. Vá para SQL Editor")
    print("3. Execute os comandos SQL mostrados acima")
    print("4. Teste a aplicação com diferentes usuários")
    print()
    print("🛡️ Após executar os comandos, seus dados estarão protegidos pela LGPD!")

