from flask import Flask, render_template, request, jsonify, redirect, url_for
from datetime import datetime
import database as db
import pandas as pd
import os

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Rota do Painel Inicial
@app.route('/')
def index():
    vendedores = db.get_all_vendedores()
    vendas = db.get_all_vendas()
    
    # Calcula dados do mês atual
    hoje = datetime.now()
    mes_atual = hoje.month
    ano_atual = hoje.year
    
    total_vendas_mes = 0.0
    total_comissoes_mes = 0.0
    ranking = {}
    
    for venda in vendas:
        data_venda = datetime.strptime(venda['data'], '%Y-%m-%d')
        if data_venda.month == mes_atual and data_venda.year == ano_atual:
            total_vendas_mes += venda['valor']
            total_comissoes_mes += venda['valor_comissao']
            
            vendedor = venda['vendedor_nome']
            ranking[vendedor] = ranking.get(vendedor, 0.0) + venda['valor']
    
    total_geral_vendas = sum(v['total_vendido'] for v in vendedores)
    ranking_sorted = sorted(ranking.items(), key=lambda item: item[1], reverse=True)[:3]
    
    return render_template('index.html', 
                         total_vendas_mes=total_vendas_mes,
                         total_comissoes_mes=total_comissoes_mes,
                         total_geral_vendas=total_geral_vendas,
                         ranking=ranking_sorted,
                         vendas=vendas) # Adicionando a lista de vendas para o template index.html

# Rota de Vendedores
@app.route('/vendedores')
def vendedores():
    vendedores = db.get_all_vendedores()
    return render_template('vendedores.html', vendedores=vendedores)

@app.route('/api/vendedor/add', methods=['POST'])
def add_vendedor():
    data = request.json
    nome = data.get('nome', '').strip()
    comissao = data.get('comissao', 0)
    
    if not nome or comissao < 0 or comissao > 100:
        return jsonify({'success': False, 'message': 'Dados inválidos'}), 400
    
    if db.add_vendedor(nome, comissao):
        return jsonify({'success': True, 'message': f'Vendedor {nome} cadastrado com sucesso'})
    else:
        return jsonify({'success': False, 'message': f'Vendedor com nome {nome} já existe'}), 400

# Rota de Clientes
@app.route('/clientes')
def clientes():
    clientes = db.get_all_clientes()
    return render_template('clientes.html', clientes=clientes)

@app.route('/api/cliente/add', methods=['POST'])
def add_cliente():
    data = request.json
    nome = data.get('nome', '').strip()
    telefone = data.get('telefone', '').strip()
    
    if not nome:
        return jsonify({'success': False, 'message': 'Nome é obrigatório'}), 400
    
    if db.add_cliente(nome, telefone):
        return jsonify({'success': True, 'message': f'Cliente {nome} cadastrado com sucesso'})
    else:
        return jsonify({'success': False, 'message': f'Cliente com nome {nome} já existe'}), 400

# Rota de Registro de Vendas
@app.route('/vendas')
def vendas():
    vendedores = db.get_all_vendedores()
    clientes = db.get_all_clientes()
    return render_template('vendas.html', vendedores=vendedores, clientes=clientes, now=datetime.now())

@app.route('/api/venda/add', methods=['POST'])
def add_venda():
    data = request.json
    vendedor_id = data.get('vendedor_id')
    cliente_id = data.get('cliente_id')
    valor = data.get('valor', 0)
    comissao_manual = data.get('comissao_manual')
    
    try:
        valor = float(valor)
        if valor <= 0:
            raise ValueError
    except (ValueError, TypeError):
        return jsonify({'success': False, 'message': 'Valor inválido'}), 400
    
    vendedor = db.get_vendedor_by_id(vendedor_id)
    cliente = db.get_cliente_by_id(cliente_id)
    
    if not vendedor or not cliente:
        return jsonify({'success': False, 'message': 'Vendedor ou Cliente não encontrado'}), 400
    
    comissao_aplicada = comissao_manual if comissao_manual else vendedor['comissao_percentual']
    
    try:
        comissao_aplicada = float(comissao_aplicada)
        if comissao_aplicada < 0 or comissao_aplicada > 100:
            raise ValueError
    except (ValueError, TypeError):
        return jsonify({'success': False, 'message': 'Comissão inválida'}), 400
    
    valor_comissao = valor * (comissao_aplicada / 100.0)
    data_venda = datetime.now().strftime('%Y-%m-%d')
    
    db.add_venda(vendedor_id, cliente_id, valor, data_venda, comissao_aplicada, valor_comissao)
    
    return jsonify({'success': True, 'message': f'Venda registrada! {vendedor["nome"]} ganhou R$ {valor_comissao:.2f} de comissão'})

# Rota de Relatórios
@app.route('/relatorios')
def relatorios():
    mes_ano = request.args.get('mes_ano', datetime.now().strftime('%Y-%m'))
    
    try:
        data_obj = datetime.strptime(mes_ano, '%Y-%m')
        start_date = data_obj.strftime('%Y-%m-01')
        
        if data_obj.month == 12:
            end_date = datetime(data_obj.year + 1, 1, 1).strftime('%Y-%m-%d')
        else:
            end_date = datetime(data_obj.year, data_obj.month + 1, 1).strftime('%Y-%m-%d')
        
        vendas = db.get_vendas_by_period(start_date, end_date)
    except ValueError:
        vendas = db.get_all_vendas()
    
    total_vendido = sum(v['valor'] for v in vendas)
    total_comissoes = sum(v['valor_comissao'] for v in vendas)
    
    ranking = {}
    for venda in vendas:
        vendedor = venda['vendedor_nome']
        valor = venda['valor']
        ranking[vendedor] = ranking.get(vendedor, 0.0) + valor
    
    ranking_sorted = sorted(ranking.items(), key=lambda item: item[1], reverse=True)
    
    return render_template('relatorios.html', 
                         vendas=vendas,
                         total_vendido=total_vendido,
                         total_comissoes=total_comissoes,
                         ranking=ranking_sorted,
                         mes_ano=mes_ano)

@app.route('/api/venda/update/<int:venda_id>', methods=['PUT'])
def update_venda(venda_id):
    data = request.json
    valor = data.get('valor', 0)
    comissao = data.get('comissao', 0)
    
    try:
        valor = float(valor)
        comissao = float(comissao)
        if valor <= 0 or comissao < 0 or comissao > 100:
            raise ValueError
    except (ValueError, TypeError):
        return jsonify({'success': False, 'message': 'Dados inválidos'}), 400
    
    valor_comissao = valor * (comissao / 100.0)
    
    if db.update_venda(venda_id, valor, comissao, valor_comissao):
        return jsonify({'success': True, 'message': 'Venda atualizada com sucesso'})
    else:
        return jsonify({'success': False, 'message': 'Erro ao atualizar venda'}), 400

@app.route('/api/venda/delete/<int:venda_id>', methods=['DELETE'])
def delete_venda(venda_id):
    if db.delete_venda(venda_id):
        return jsonify({'success': True, 'message': 'Venda excluída com sucesso'})
    else:
        return jsonify({'success': False, 'message': 'Erro ao excluir venda'}), 400

# Rota de Exportação
@app.route('/exportar')
def exportar():
    vendas = db.get_all_vendas()
    
    if not vendas:
        return jsonify({'success': False, 'message': 'Não há vendas para exportar'}), 400
    
    df = pd.DataFrame(vendas)
    
    df.rename(columns={
        'id': 'ID_Venda',
        'vendedor_nome': 'Vendedor',
        'cliente_nome': 'Cliente',
        'valor': 'Valor_Venda',
        'data': 'Data',
        'comissao_aplicada': 'Comissao_Percentual',
        'valor_comissao': 'Valor_Comissao'
    }, inplace=True)
    
    df = df[['ID_Venda', 'Data', 'Vendedor', 'Cliente', 'Valor_Venda', 'Comissao_Percentual', 'Valor_Comissao']]
    
    filename = f"relatorio_vendas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    try:
        df.to_csv(filename, index=False, sep=';', decimal=',', encoding='utf-8-sig')
        return jsonify({'success': True, 'message': f'Arquivo {filename} gerado com sucesso', 'filename': filename})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao exportar: {str(e)}'}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
