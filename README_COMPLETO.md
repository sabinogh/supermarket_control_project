# 🛒 Sistema de Controle de Compras de Supermercado

## 📋 Sobre o Projeto

Sistema completo para controle pessoal de gastos em supermercados, desenvolvido em Streamlit com autenticação segura via Supabase. O sistema permite que usuários registrem suas compras, analisem seus gastos e contribuam com uma base comunitária de mercados, tudo isso respeitando a LGPD (Lei Geral de Proteção de Dados).

## ✨ Funcionalidades Principais

### 🔐 Sistema de Autenticação
- **Registro e login seguros** com Supabase Auth
- **Isolamento completo de dados** por usuário
- **Perfis de administrador** com acesso a dados agregados
- **Conformidade total com LGPD**

### 👤 Para Usuários
- **Registrar compras pessoais** com detalhamento de itens
- **Analisar gastos** com gráficos e relatórios
- **Dashboard personalizado** com métricas e tendências
- **Exportar dados** em formato CSV
- **Adicionar mercados** à base comunitária

### 🔑 Para Administradores
- **Dashboard administrativo** com estatísticas gerais
- **Dados agregados** sem acesso a informações pessoais
- **Monitoramento de uso** respeitando a privacidade

### 🤝 Funcionalidades Comunitárias
- **Base compartilhada de mercados** entre todos os usuários
- **Contribuição colaborativa** para melhorar a base de dados
- **Filtros avançados** por cidade e estado

## 🛡️ Segurança e Privacidade

### Proteção de Dados
- **RLS (Row Level Security)** implementado no banco de dados
- **Autenticação JWT** via Supabase
- **Isolamento total** entre dados de diferentes usuários
- **Criptografia** de senhas e tokens

### Conformidade LGPD
- **Transparência** sobre coleta e uso de dados
- **Minimização** - apenas dados necessários são coletados
- **Finalidade específica** - dados usados apenas para controle de gastos
- **Direitos do titular** - acesso, portabilidade e exclusão de dados

## 🚀 Instalação Rápida

### 1. Pré-requisitos
- Python 3.11+
- Conta no Supabase

### 2. Configuração
```bash
# Instale dependências
pip install -r requirements.txt

# Configure variáveis de ambiente (.env)
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_KEY=sua_chave_publica
ADMIN_EMAILS=admin@exemplo.com
```

### 3. Configure o Banco de Dados
Execute os comandos SQL fornecidos em `setup_database_security.py` no Supabase Dashboard.

### 4. Execute
```bash
# Teste a configuração
python test_authentication.py

# Execute a aplicação
streamlit run 0_Página_Inicial.py
```

## 📁 Estrutura do Projeto

```
📁 supermarket_control_project/
├── 0_Página_Inicial.py              # Página principal com controle de acesso
├── pages/
│   ├── Login.py                     # Sistema de autenticação
│   ├── 1_Registrar_Compras.py       # Registro de compras pessoais
│   ├── 2_Analisar_Compras.py        # Análise de gastos pessoais
│   ├── 3_Mercados.py                # Gerenciamento comunitário de mercados
│   └── 4_Dashboard_Analise.py       # Dashboard com análises avançadas
├── services/
│   ├── supabase_client.py           # Cliente Supabase e autenticação
│   └── db_queries.py                # Consultas ao banco de dados
├── setup_database_security.py       # Configuração de segurança RLS
├── test_authentication.py           # Testes automatizados
├── GUIA_INSTALACAO.md               # Guia rápido de instalação
├── documentacao_sistema_autenticacao.md  # Documentação completa
├── requirements.txt                 # Dependências Python
└── .env                            # Variáveis de ambiente
```

## 🔧 Tecnologias Utilizadas

- **Frontend:** Streamlit
- **Backend:** Supabase (PostgreSQL + Auth)
- **Visualizações:** Plotly
- **Autenticação:** Supabase Auth (OAuth 2.0)
- **Segurança:** Row Level Security (RLS)
- **Deploy:** Streamlit Cloud / Heroku / Railway

## 📊 Funcionalidades por Página

### 🏠 Página Inicial
- Controle de acesso automático
- Redirecionamento baseado em autenticação
- Menu personalizado por perfil de usuário

### 🔐 Login
- Registro de novos usuários
- Login com email e senha
- Recuperação de senha
- Validação e tratamento de erros

### 📝 Registrar Compras
- Formulário intuitivo para registro
- Seleção de mercados da base comunitária
- Adição de múltiplos itens por compra
- Cálculo automático de totais

### 📊 Analisar Compras
- Filtros por período e mercado
- Tabela detalhada de compras
- Métricas resumo (total gasto, ticket médio)
- Gráficos interativos
- Export para CSV

### 🏪 Mercados
- Visualização de todos os mercados cadastrados
- Filtros por cidade e estado
- Adição de novos estabelecimentos
- Funcionalidade comunitária

### 📈 Dashboard
- **Usuários:** Análises pessoais avançadas
- **Admins:** Estatísticas agregadas do sistema
- Múltiplas visualizações (pizza, linha, barras)
- Análises temporais e por categoria

## 🧪 Testes

O projeto inclui testes automatizados para verificar:
- Conectividade com Supabase
- Funções de autenticação
- Estrutura do banco de dados
- Variáveis de ambiente

```bash
python test_authentication.py
```

## 📈 Métricas Disponíveis

### Para Usuários
- Total gasto por período
- Número de compras realizadas
- Ticket médio de compras
- Gastos por mercado
- Evolução temporal dos gastos
- Top itens mais comprados

### Para Administradores
- Volume total de vendas (agregado)
- Número total de compras (anônimo)
- Mercados mais utilizados
- Tendências de crescimento da plataforma

## 🔒 Política de Privacidade

### Dados Coletados
- **Email:** Para autenticação (obrigatório)
- **Compras:** Data, mercado, itens, valores (pessoal)
- **Mercados:** Informações de estabelecimentos (comunitário)

### Dados NÃO Coletados
- Informações pessoais além do email
- Dados de localização
- Informações de pagamento
- Dados de terceiros

### Uso dos Dados
- **Finalidade única:** Controle pessoal de gastos
- **Não compartilhamento:** Dados pessoais são privados
- **Agregação:** Apenas estatísticas anônimas para administração

## 📞 Suporte

- **Documentação completa:** `documentacao_sistema_autenticacao.md`
- **Guia de instalação:** `GUIA_INSTALACAO.md`
- **Testes:** `python test_authentication.py`

## 🎯 Roadmap

### Próximas Funcionalidades
- [ ] Categorização de produtos
- [ ] Relatórios mensais automáticos
- [ ] Notificações por email
- [ ] API REST para integração
- [ ] App mobile (React Native)
- [ ] Comparação de preços entre mercados

### Melhorias Técnicas
- [ ] Cache Redis para performance
- [ ] Testes unitários completos
- [ ] CI/CD automatizado
- [ ] Monitoramento com Sentry
- [ ] Backup automático de dados

---

## 📄 Licença / License

**Português**  
Este projeto **não possui licença open source**.  
O uso, cópia, modificação ou distribuição deste código só é permitido mediante autorização explícita do autor.  

© 2025 Guilherme H. Sabino. Todos os direitos reservados.  

---

**English**  
This project **does not have an open source license**.  
Use, copying, modification, or distribution of this code is only allowed with the explicit permission of the author.  

© 2025 Guilherme H. Sabino. All rights reserved.

---

**Desenvolvido com ❤️ e foco em privacidade e segurança** 🛡️

**Conforme LGPD | Dados protegidos | Sistema seguro**

