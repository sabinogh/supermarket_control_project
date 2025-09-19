# 🚀 Guia Rápido de Instalação - Sistema de Autenticação

## ⚡ Instalação Rápida

### 1. Pré-requisitos
- Python 3.11+
- Conta no Supabase
- Git (opcional)

### 2. Configuração do Supabase

1. **Crie um projeto no Supabase:**
   - Acesse [supabase.com](https://supabase.com)
   - Crie uma nova organização/projeto
   - Anote a URL e a chave pública (anon key)

2. **Configure as tabelas no SQL Editor:**
```sql
-- Habilitar autenticação
-- (Já vem habilitado por padrão)

-- Adicionar colunas user_id às tabelas existentes
ALTER TABLE mercados 
ADD COLUMN IF NOT EXISTS added_by_user_id UUID REFERENCES auth.users(id);

ALTER TABLE compras_itens 
ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES auth.users(id);

-- Habilitar RLS
ALTER TABLE compras_itens ENABLE ROW LEVEL SECURITY;

-- Políticas para compras_itens
CREATE POLICY "Users can view own purchases" ON compras_itens
FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own purchases" ON compras_itens
FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own purchases" ON compras_itens
FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own purchases" ON compras_itens
FOR DELETE USING (auth.uid() = user_id);

-- Políticas para mercados (dados compartilhados)
CREATE POLICY "Everyone can view markets" ON mercados
FOR SELECT USING (true);

CREATE POLICY "Authenticated users can insert markets" ON mercados
FOR INSERT WITH CHECK (auth.uid() = added_by_user_id);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_compras_itens_user_id ON compras_itens(user_id);
CREATE INDEX IF NOT EXISTS idx_mercados_added_by_user_id ON mercados(added_by_user_id);
```

### 3. Configuração da Aplicação

1. **Configure o arquivo .env:**
```bash
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_KEY=sua_chave_publica_aqui
ADMIN_EMAILS=seu-email@exemplo.com
```

2. **Instale as dependências:**
```bash
pip install -r requirements.txt
```

3. **Teste a configuração:**
```bash
python test_authentication.py
```

4. **Execute a aplicação:**
```bash
streamlit run 0_Página_Inicial.py
```

## 🔧 Configuração Avançada

### Variáveis de Ambiente Opcionais

```bash
# .env
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_KEY=sua_chave_publica
ADMIN_EMAILS=admin1@exemplo.com,admin2@exemplo.com  # Emails de administradores
```

### Configuração para Deploy

1. **Streamlit Cloud:**
   - Adicione as variáveis no painel de secrets
   - Use o formato TOML:
```toml
SUPABASE_URL = "https://seu-projeto.supabase.co"
SUPABASE_KEY = "sua_chave_publica"
ADMIN_EMAILS = "admin@exemplo.com"
```

2. **Heroku/Railway/Render:**
   - Configure as variáveis de ambiente no painel
   - Certifique-se de que `requirements.txt` está atualizado

## 🧪 Testes

### Teste Básico
```bash
python test_authentication.py
```

### Teste Manual
1. Acesse a aplicação
2. Registre um novo usuário
3. Faça login
4. Teste cada página
5. Verifique isolamento de dados

## 🚨 Solução de Problemas

### Erro: "supabase_url is required"
- Verifique se o arquivo `.env` existe
- Confirme se as variáveis estão corretas
- Para Streamlit Cloud, use o painel de secrets

### Erro: "Could not find table"
- Execute os comandos SQL no Supabase
- Verifique se as tabelas existem
- Confirme se RLS está habilitado

### Usuário não consegue ver dados
- Verifique se as políticas RLS estão criadas
- Confirme se o usuário está autenticado
- Teste com `get_user_id()` retornando valor válido

### Performance lenta
- Verifique se os índices foram criados
- Otimize queries no código
- Use cache do Streamlit quando apropriado

## 📋 Checklist de Deploy

- [ ] Projeto Supabase criado
- [ ] Tabelas configuradas com RLS
- [ ] Políticas de segurança implementadas
- [ ] Variáveis de ambiente configuradas
- [ ] Testes passando (`test_authentication.py`)
- [ ] Aplicação rodando localmente
- [ ] Deploy realizado
- [ ] Teste de registro/login em produção
- [ ] Verificação de isolamento de dados

## 🎯 Próximos Passos

Após a instalação:

1. **Configure administradores:**
   - Adicione emails na variável `ADMIN_EMAILS`
   - Teste funcionalidades administrativas

2. **Personalize a aplicação:**
   - Ajuste cores e layout
   - Adicione logo da empresa
   - Customize mensagens

3. **Monitore o uso:**
   - Acompanhe métricas no Supabase
   - Monitore logs de erro
   - Colete feedback dos usuários

4. **Expanda funcionalidades:**
   - Adicione categorias de produtos
   - Implemente relatórios avançados
   - Crie notificações por email

## 📞 Suporte

- **Documentação completa:** `documentacao_sistema_autenticacao.md`
- **Testes automatizados:** `python test_authentication.py`
- **Logs:** Disponíveis no Streamlit e Supabase Dashboard

---

**Sistema pronto para uso! 🎉**

