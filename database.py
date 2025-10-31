import sqlite3
from datetime import datetime

DATABASE_NAME = 'comissoes.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def initialize_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Tabela de Vendedores
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Vendedores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE,
            comissao_percentual REAL NOT NULL,
            total_vendido REAL DEFAULT 0.0,
            total_comissao REAL DEFAULT 0.0
        );
    """)

    # Tabela de Clientes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE,
            telefone TEXT
        );
    """)

    # Tabela de Vendas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Vendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vendedor_id INTEGER NOT NULL,
            cliente_id INTEGER NOT NULL,
            valor REAL NOT NULL,
            data TEXT NOT NULL,
            comissao_aplicada REAL NOT NULL,
            valor_comissao REAL NOT NULL,
            FOREIGN KEY (vendedor_id) REFERENCES Vendedores(id),
            FOREIGN KEY (cliente_id) REFERENCES Clientes(id)
        );
    """)

    conn.commit()
    conn.close()

# Funções CRUD para Vendedores
def add_vendedor(nome, comissao_percentual):
    conn = get_db_connection()
    try:
        conn.execute("INSERT INTO Vendedores (nome, comissao_percentual) VALUES (?, ?)", (nome, comissao_percentual))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_all_vendedores():
    conn = get_db_connection()
    vendedores = conn.execute("SELECT * FROM Vendedores ORDER BY nome").fetchall()
    conn.close()
    return [dict(vendedor) for vendedor in vendedores]

def get_vendedor_by_id(vendedor_id):
    conn = get_db_connection()
    vendedor = conn.execute("SELECT * FROM Vendedores WHERE id = ?", (vendedor_id,)).fetchone()
    conn.close()
    return dict(vendedor) if vendedor else None

def update_vendedor_totals(vendedor_id, valor_venda, valor_comissao):
    conn = get_db_connection()
    conn.execute("""
        UPDATE Vendedores
        SET total_vendido = total_vendido + ?,
            total_comissao = total_comissao + ?
        WHERE id = ?
    """, (valor_venda, valor_comissao, vendedor_id))
    conn.commit()
    conn.close()

# Funções CRUD para Clientes
def add_cliente(nome, telefone):
    conn = get_db_connection()
    try:
        conn.execute("INSERT INTO Clientes (nome, telefone) VALUES (?, ?)", (nome, telefone))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_all_clientes():
    conn = get_db_connection()
    clientes = conn.execute("SELECT * FROM Clientes ORDER BY nome").fetchall()
    conn.close()
    return [dict(cliente) for cliente in clientes]

def get_cliente_by_id(cliente_id):
    conn = get_db_connection()
    cliente = conn.execute("SELECT * FROM Clientes WHERE id = ?", (cliente_id,)).fetchone()
    conn.close()
    return dict(cliente) if cliente else None

# Funções CRUD para Vendas
def add_venda(vendedor_id, cliente_id, valor, data, comissao_aplicada, valor_comissao):
    conn = get_db_connection()
    conn.execute("""
        INSERT INTO Vendas (vendedor_id, cliente_id, valor, data, comissao_aplicada, valor_comissao)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (vendedor_id, cliente_id, valor, data, comissao_aplicada, valor_comissao))
    conn.commit()
    
    # Atualiza os totais do vendedor
    update_vendedor_totals(vendedor_id, valor, valor_comissao)
    
    conn.close()

def get_all_vendas():
    conn = get_db_connection()
    vendas = conn.execute("""
        SELECT 
            Vendas.id, Vendas.valor, Vendas.data, Vendas.comissao_aplicada, Vendas.valor_comissao,
            Vendedores.nome AS vendedor_nome, Vendedores.id AS vendedor_id,
            Clientes.nome AS cliente_nome
        FROM Vendas
        JOIN Vendedores ON Vendas.vendedor_id = Vendedores.id
        JOIN Clientes ON Vendas.cliente_id = Clientes.id
        ORDER BY Vendas.data DESC
    """).fetchall()
    conn.close()
    return [dict(venda) for venda in vendas]

def get_vendas_by_period(start_date=None, end_date=None):
    conn = get_db_connection()
    query = """
        SELECT 
            Vendas.id, Vendas.valor, Vendas.data, Vendas.comissao_aplicada, Vendas.valor_comissao,
            Vendedores.nome AS vendedor_nome, Vendedores.id AS vendedor_id,
            Clientes.nome AS cliente_nome
        FROM Vendas
        JOIN Vendedores ON Vendas.vendedor_id = Vendedores.id
        JOIN Clientes ON Vendas.cliente_id = Clientes.id
    """
    params = []
    
    if start_date and end_date:
        query += " WHERE Vendas.data BETWEEN ? AND ?"
        params = [start_date, end_date]
    elif start_date:
        query += " WHERE Vendas.data >= ?"
        params = [start_date]
    elif end_date:
        query += " WHERE Vendas.data <= ?"
        params = [end_date]
        
    query += " ORDER BY Vendas.data DESC"
    
    vendas = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(venda) for venda in vendas]

def update_venda(venda_id, novo_valor, nova_comissao, novo_valor_comissao):
    conn = get_db_connection()
    
    # Busca a venda atual
    venda = conn.execute("SELECT vendedor_id, valor, valor_comissao FROM Vendas WHERE id = ?", (venda_id,)).fetchone()
    
    if venda:
        vendedor_id = venda['vendedor_id']
        valor_antigo = venda['valor']
        comissao_antiga = venda['valor_comissao']
        
        # Calcula a diferença
        diferenca_valor = novo_valor - valor_antigo
        diferenca_comissao = novo_valor_comissao - comissao_antiga
        
        # Atualiza a venda
        conn.execute("""
            UPDATE Vendas
            SET valor = ?, comissao_aplicada = ?, valor_comissao = ?
            WHERE id = ?
        """, (novo_valor, nova_comissao, novo_valor_comissao, venda_id))
        
        # Atualiza os totais do vendedor
        conn.execute("""
            UPDATE Vendedores
            SET total_vendido = total_vendido + ?,
                total_comissao = total_comissao + ?
            WHERE id = ?
        """, (diferenca_valor, diferenca_comissao, vendedor_id))
        
        conn.commit()
        conn.close()
        return True
    
    conn.close()
    return False

def delete_venda(venda_id):
    conn = get_db_connection()
    
    venda = conn.execute("SELECT vendedor_id, valor, valor_comissao FROM Vendas WHERE id = ?", (venda_id,)).fetchone()
    
    if venda:
        vendedor_id, valor, valor_comissao = venda['vendedor_id'], venda['valor'], venda['valor_comissao']
        
        conn.execute("""
            UPDATE Vendedores
            SET total_vendido = total_vendido - ?,
                total_comissao = total_comissao - ?
            WHERE id = ?
        """, (valor, valor_comissao, vendedor_id))
        
        conn.execute("DELETE FROM Vendas WHERE id = ?", (venda_id,))
        conn.commit()
        conn.close()
        return True
    
    conn.close()
    return False

# Inicializa o banco de dados ao importar o módulo
initialize_db()
