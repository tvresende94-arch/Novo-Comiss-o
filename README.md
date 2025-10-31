# Controle de Comissão de Vendas - Versão Web

Esta é uma aplicação web desenvolvida em **Python com Flask** para gerenciar vendedores, clientes, registrar vendas, calcular comissões e gerar relatórios mensais. A aplicação é totalmente responsiva e pode ser acessada de qualquer navegador.

## Requisitos

Para executar esta aplicação, você precisa ter o **Python 3** instalado em seu sistema.

## Instalação e Execução

Siga os passos abaixo para configurar e rodar a aplicação:

### 1. Navegue até o diretório do projeto

```bash
cd comissao_app_web
```

### 2. Instale as dependências necessárias

A aplicação utiliza as bibliotecas `Flask` (framework web) e `pandas` (para exportação em CSV).

```bash
pip install flask pandas
```

### 3. Execute a aplicação

```bash
python app.py
```

### 4. Acesse a aplicação no navegador

Abra seu navegador (Chrome, Firefox, Edge, Safari, etc.) e acesse:

```
http://localhost:5000
```

A aplicação estará pronta para uso!

## Funcionalidades

A aplicação oferece as seguintes funcionalidades principais:

### 1. Painel Inicial
*   Mostra o **Total de Vendas do Mês** e **Total de Comissões do Mês**.
*   Exibe o **Ranking Top 3 Vendedores** do mês.
*   Contém botões de ação rápida para as principais tarefas.

### 2. Vendedores
*   **Cadastro:** Permite cadastrar novos vendedores com nome e a porcentagem de comissão padrão.
*   **Acompanhamento:** Exibe o total vendido e o total de comissão acumulada por cada vendedor.

### 3. Clientes
*   **Cadastro:** Permite cadastrar clientes com nome e telefone.

### 4. Registrar Venda
*   Permite registrar uma venda associando um vendedor e um cliente.
*   O valor da comissão é calculado automaticamente com base na porcentagem do vendedor, mas pode ser alterado manualmente no momento do registro.
*   A data da venda é registrada automaticamente.

### 5. Relatórios
*   Permite visualizar o histórico de todas as vendas.
*   **Filtro:** É possível filtrar as vendas por mês e ano (formato AAAA-MM).
*   **Resumo:** Exibe o total vendido, total de comissões e o melhor vendedor para o período filtrado.
*   **Exclusão:** Permite excluir vendas individualmente, com confirmação, revertendo automaticamente a comissão e o total vendido do vendedor.

### 6. Exportar Dados
*   Permite exportar o histórico completo de vendas para um arquivo **CSV** (separado por ponto e vírgula), que pode ser aberto em qualquer planilha eletrônica (Excel, Google Sheets, etc.). O arquivo é salvo no mesmo diretório da aplicação.

## Persistência de Dados

Todos os dados (Vendedores, Clientes e Vendas) são armazenados no arquivo `comissoes.db` (banco de dados SQLite) e são **mantidos permanentemente** mesmo após o fechamento da aplicação.

## Estrutura do Projeto

```
comissao_app_web/
├── app.py                    # Arquivo principal com as rotas Flask
├── database.py               # Módulo de gerenciamento do banco de dados SQLite
├── README.md                 # Este arquivo
├── comissoes.db              # Banco de dados (criado automaticamente)
├── templates/                # Pasta com os templates HTML
│   ├── base.html            # Template base com navbar e footer
│   ├── index.html           # Painel Inicial
│   ├── vendedores.html      # Painel de Vendedores
│   ├── clientes.html        # Painel de Clientes
│   ├── vendas.html          # Painel de Registro de Vendas
│   └── relatorios.html      # Painel de Relatórios
└── static/                   # Pasta com arquivos estáticos
    └── css/
        └── style.css        # Estilos CSS da aplicação
```

## Dicas de Uso

*   **Primeira vez:** Comece cadastrando alguns vendedores e clientes antes de registrar vendas.
*   **Filtro de Relatórios:** Use o formato AAAA-MM (ex: 2025-10) para filtrar vendas por mês.
*   **Exportação:** Os arquivos CSV são salvos no mesmo diretório onde você executou `python app.py`.

## Troubleshooting

### Erro: "ModuleNotFoundError: No module named 'flask'"

Certifique-se de ter instalado as dependências:
```bash
pip install flask pandas
```

### Erro: "Port 5000 is already in use"

A porta 5000 já está sendo usada por outro programa. Você pode:
1. Fechar o outro programa que está usando a porta.
2. Ou modificar a porta no arquivo `app.py` (última linha):
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Mude para 5001 ou outra porta
```

### Banco de dados não está sendo criado

O arquivo `comissoes.db` é criado automaticamente na primeira execução. Se não for criado, verifique se você tem permissão de escrita no diretório.

---

Desenvolvido por Manus AI | © 2025 Controle de Comissão de Vendas
