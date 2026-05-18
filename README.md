# Rateio API - Backend

O **Rateio** é uma plataforma desenvolvida para simplificar a gestão financeira, divisão de despesas e organização de tarefas cotidianas em moradias compartilhadas (repúblicas universitárias, apartamentos divididos, etc.).

Este repositório contém a **API RESTful** do projeto, garantindo o processamento das regras de negócio, persistência de dados, cálculo automático de rateios e uma arquitetura segura para o consumo do aplicativo mobile.


## Tecnologias Utilizadas

* **Linguagem & Framework:** Python 3, Django
* **API:** Django REST Framework (DRF)
* **Banco de Dados:** MySQL
* **Processamento de Imagens:** Pillow (Upload de Comprovantes/Recibos)
* **Segurança:** Autenticação JWT (JSON Web Tokens) via SimpleJWT


## Arquitetura e Segurança

Pensando nas melhores práticas de mercado e em fundamentos de cibersegurança, a API possui suas rotas protegidas de ponta a ponta. O sistema exige a geração de um *Bearer Token* (Access/Refresh) para garantir que apenas moradores autenticados acessem, alterem ou auditem os dados financeiros e organizacionais da sua respectiva república.

## 🚀 Como rodar o projeto localmente

Siga os passos abaixo para testar a API na sua máquina:

1. **Clone o repositório:**
   ```bash
   git clone [https://github.com/SEU_USUARIO/rateio-backend.git](https://github.com/SEU_USUARIO/rateio-backend.git)
   cd rateio-backend

2. Crie e ative o ambiente virtual:

   ```bash
   python -m venv venv

   # No Windows:
   venv\Scripts\activate

   # No Linux/Mac:
   source venv/bin/activate

3. Instale as dependências:

   ```bash
   pip install -r requirements.txt

4. Configure o Banco de Dados:

- Certifique-se de ter o MySQL rodando localmente.

- Crie um banco de dados chamado app_rep no seu MySQL.

Atenção: Verifique as credenciais (usuário e senha) no arquivo settings.py para garantir que o Django consiga se conectar ao seu banco.

5. Rode as migrações (Criação das tabelas):

   ```bash
   python manage.py makemigrations
   python manage.py migrate

6. Inicie o servidor local:

   ```bash
   python manage.py runserver
   
A API estará rodando em http://localhost:8000/api/. Quando arquivos de imagem forem enviados pelo aplicativo, eles serão salvos automaticamente na pasta local /media/.
