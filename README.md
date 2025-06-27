# TFC
# Interface Azure para ERP

![](Arquitetura_da_Solucao.png?raw=true "Arquitetura")

## 📌 Sobre o Projeto

A **Interface Azure para ERP** é uma API que permite a integração automatizada entre sistemas ERP-GRH e o Microsoft Azure, facilitando a gestão de utilizadores, permissões e recursos cloud. A solução reduz a complexidade operacional, melhora a segurança e automatiza processos que normalmente exigiriam intervenção manual.

## 🚀 Funcionalidades

✅ Gestão centralizada de acessos ao **Microsoft 365** (Outlook, SharePoint, Teams, etc.)  
✅ Automação da configuração de **máquinas virtuais (VMs), Azure SQL e AVDs**  
✅ Conformidade com regulamentos como **GDPR**  
✅ **API** documentada e extensível  

## 🛠️ Tecnologias Utilizadas

- **Python** (FastAPI) - Desenvolvimento da API  
- **JavaSprit** Desenvolvimento do UserInterface de teste
- **Microsoft Azure** (Entra ID, Key Vault, Graph API)  
- **Bsase de Dados** - MySQL  
- **ERP-GRH** (Sistema externo conectado via API)  
- **OrangeHRM** (Human resource management system)  
    


## 📂 Estrutura do Repositório

```bash
📦 Interface-Azure-ERP
├── 📜 README.md
├── 📜 requirements.txt  # Dependências do projeto
├── 📜 azure_integration.py  # Arquivo principal da API ligada ao Azure
├── 📜 main.py  # Arquivo principal da API que liga a uma BD (OrangeHRM)
├── 📂 static/  # UserInterface css
└── 📂 templates/ # UserInterface  html
