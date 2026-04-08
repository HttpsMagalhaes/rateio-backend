# Rateio API - Backend

O **Rateio** é uma plataforma desenvolvida para simplificar a gestão financeira, divisão de despesas e organização de tarefas cotidianas em moradias compartilhadas (repúblicas universitárias, divisões de apartamento, etc.).

Este repositório contém a **API RESTful** do projeto, garantindo o processamento de regras de negócio, persistência de dados e uma arquitetura segura para o consumo do aplicativo mobile (Frontend).

## Tecnologias Utilizadas

* **Linguagem & Framework:** Python 3, Django
* **API:** Django REST Framework
* **Banco de Dados:** MySQL
* **Segurança:** Autenticação JWT (JSON Web Tokens) via `SimpleJWT`

## Arquitetura e Segurança

Pensando nas melhores práticas de mercado e em fundamentos de cibersegurança, a API possui suas rotas protegidas. O sistema exige a geração de um *Bearer Token* (Access/Refresh) para garantir que apenas moradores autenticados acessem ou modifiquem os dados financeiros e organizacionais da república.

## Como rodar o projeto localmente

Siga os passos abaixo para testar a API na sua máquina:

1. **Clone o repositório:**
   ```bash
   git clone [https://github.com/SEU_USUARIO/rateio-backend.git](https://github.com/SEU_USUARIO/rateio-backend.git)
   cd rateio-backend

2. **Crie e ative o ambiente virtual:**
   ```bash
    python -m venv venv
    # No Windows:
    venv\Scripts\activate
    # No Linux/Mac:
    source venv/bin/activate

3. **Instale as dependências:**
   ```bash
    pip install -r requirements.txt

4. **Configure o Banco de Dados (MySQL):**
   Crie um banco chamado app_rep no seu MySQL local.
   
   Rode as migrações para gerar as tabelas:
   ```bash
   python manage.py migrate
   
 5 . ** Inicie o servidor local:**
  ```bash
   python manage.py runserver
