# Supermarket Control Project

📊 Overview
A comprehensive Business Intelligence application demonstrating how to transform raw data into strategic insights that drive business decisions. Built with modern technologies and following industry best practices in data analysis, security, and visualization.
This project showcases end-to-end BI capabilities including data collection, statistical analysis, forecasting with machine learning, and interactive dashboards—all applicable to real-world corporate scenarios.
Key Features:

📈 Advanced Analytics: Price variation analysis, trend identification, statistical metrics
🔮 Forecasting: 6-month projection using linear regression
🔒 Enterprise Security: Row Level Security (RLS), authentication, LGPD compliance
📊 Interactive Dashboards: Real-time filters, dynamic visualizations with Plotly
🗄️ Scalable Architecture: PostgreSQL backend, optimized queries, caching strategies

🎯 Project Purpose
While using supermarket purchases as a practical and accessible scenario, this project demonstrates Business Intelligence principles applicable to any corporate environment:

Cost Control & Financial Planning
Procurement Analytics & Supplier Management
Pricing Strategy & Market Analysis
Budget Forecasting & Resource Optimization
Supply Chain Analytics

The focus is on showcasing analytical methodology, technical implementation, and business value generation—not on the specific domain.

🛠️ Technology Stack
Backend & Database:

Python 3.11+ - Core language for application logic and data processing
Supabase (PostgreSQL) - Robust database with built-in authentication and Row Level Security
Pandas & NumPy - Data manipulation and statistical operations
Scikit-learn - Machine learning for forecasting models

Frontend & Visualization:

Streamlit - Interactive web interface with reactive components
Plotly - Interactive charts with tooltips, zoom, and filters

Security & Governance:

Row Level Security (RLS) for multi-user data isolation
JWT-based authentication via Supabase Auth
LGPD compliance (Brazilian data protection regulation)

🚀 Key Capabilities
1. Price Variation Analysis
Identifies items with highest price volatility through percentage calculation between purchases, enabling strategic procurement decisions and supplier negotiation.
2. Forecasting with Linear Regression
Projects spending for the next 6 months based on historical trends, supporting financial planning and budget allocation.
3. Temporal Trend Analysis
Reveals spending patterns and seasonality through monthly aggregations, detecting anomalies and enabling period-over-period comparisons.
4. Statistical Metrics
Automatically calculates average, maximum, minimum prices and purchase frequency for each item, generating benchmarks for cost control.

📐 Architecture
┌──────────────────────────────────────┐
│     PRESENTATION LAYER               │
│        (Streamlit)                   │
│  • Interactive dashboards            │
│  • Dynamic filters                   │
└──────────────┬───────────────────────┘
               │
┌──────────────▼───────────────────────┐
│     APPLICATION LAYER                │
│        (Python)                      │
│  • Business logic                    │
│  • Statistical calculations          │
│  • ML forecasting                    │
└──────────────┬───────────────────────┘
               │
┌──────────────▼───────────────────────┐
│     DATA LAYER                       │
│   (Supabase/PostgreSQL)              │
│  • Secure storage                    │
│  • Row Level Security                │
│  • Automatic APIs                    │
└──────────────────────────────────────┘

💼 Corporate Applications
The methodologies and techniques demonstrated in this project are directly transferable to:
Data Centers: Energy consumption monitoring, supplier cost analysis, OPEX projections
Technology: License cost analysis, cloud provider comparison, infrastructure forecasting
Manufacturing: Raw material price monitoring, lead time analysis, inventory projections
Retail: Sales analysis by store, product seasonality, demand forecasting
Finance: Departmental expenses, fixed cost variations, budget projections

📚 Complete Documentation
For comprehensive documentation including methodology, architectural decisions, challenges overcome, and detailed implementation guides, visit:
🔗 Complete Project Documentation (Notion)
The documentation covers:

Detailed analytical methodology and KPI definitions
Technical architecture and stack decisions
Security implementation and data governance
Real-world corporate applications
Lessons learned and best practices
Visual diagrams and examples

🎓 Learning Outcomes
This project demonstrates proficiency in:
Technical Skills:

End-to-end BI solution development
Data modeling and dimensional analysis
Statistical analysis and machine learning
Dashboard creation and data visualization
Database security (RLS) and authentication
Query optimization and performance tuning

Strategic Skills:

Translating business needs into technical solutions
KPI definition and strategic metric selection
Data-driven decision-making frameworks
Stakeholder communication and insight presentation

🔐 Security & Privacy

Row Level Security (RLS): Database-level isolation ensures users only access their own data
Authentication: Secure email/password authentication via Supabase Auth
Data Encryption: HTTPS in transit, encryption at rest via Supabase
LGPD Compliance: Follows Brazilian data protection regulations
No Sensitive Data Sharing: Only non-sensitive marketplace data is community-shared

👤 Author
Guilherme Henrique Sabino

Business Intelligence Analyst
Specialized in transforming data into strategic insights
Focus: Financial Analysis, Cost Control, Data-Driven Decision Making


##📄 License
Proprietary License
This project does not have an open source license. Use, copying, modification, or distribution of this code is only allowed with explicit permission from the author.
© 2025 Guilherme H. Sabino. All rights reserved.
For collaboration inquiries or permission requests, please contact via email or LinkedIn.

##🌟 Acknowledgments
This project was developed to demonstrate professional competencies in Business Intelligence and is part of a portfolio showcasing data analysis, strategic thinking, and technical implementation skills applicable to real-world business scenarios.

Note: This is a portfolio/demonstration project. The supermarket scenario serves as an accessible example to illustrate Business Intelligence principles that are universally applicable across industries and business functions.