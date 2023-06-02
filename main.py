import pandas as pd
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
import yfinance as yf

app = Flask(__name__)

CORS(app)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# Carregar os dados dos arquivos CSV durante a inicialização do aplicativo
df_fundamentos = pd.read_csv('fundamentos_empresas.csv',
                             sep=';',
                             encoding='utf-8')
df_indicadores = pd.read_csv('fundamentos_empresas_indicadores.csv',
                             sep=';',
                             encoding='utf-8')


@app.route('/')
def index():
  return 'Essa é a API de Análise de Dados do Ibovespa. Seja bem-vindo!'


@app.route('/api/dados', methods=['GET'])
def listar_todos_dados():
  json_data = df_fundamentos.to_json(orient='records')
  return jsonify(json_data)


@app.route('/api/v1/dados/<empresa>', methods=['GET'])
def consultar_dados_empresa(empresa):
  # Filtrar os dados da empresa desejada no DataFrame "df_fundamentos"
  dados_empresa = df_fundamentos[df_fundamentos['Empresa'] == empresa]

  # Verificar se a empresa existe no DataFrame
  if dados_empresa.empty:
    return f'Empresa "{empresa}" não encontrada.', 404

  # Converter os dados para um formato adequado para o JSON
  dados_json = dados_empresa.to_dict(orient='records')

  return jsonify(dados_json)


@app.route('/api/v1/dados', methods=['GET'])
def listar_dados():
  # Obter os parâmetros da query string
  empresa = request.args.get('empresa')
  coluna = request.args.get('coluna')

  # Verificar se os parâmetros foram fornecidos
  if empresa is None or coluna is None:
    return 'Parâmetros "empresa" e "coluna" devem ser fornecidos na query string.', 400

  # Filtrar os dados da empresa desejada no DataFrame "df_fundamentos"
  dados_empresa = df_fundamentos[df_fundamentos['Empresa'] == empresa]

  # Verificar se a empresa existe no DataFrame
  if dados_empresa.empty:
    return f'Empresa "{empresa}" não encontrada.', 404

  # Verificar se a coluna existe no DataFrame
  if coluna not in dados_empresa.columns:
    return f'Coluna "{coluna}" não encontrada.', 404

  # Selecionar as colunas desejadas, incluindo a coluna "Data"
  dados_colunas = dados_empresa[['Data', coluna]]

  # Converter os dados para um formato adequado para o JSON
  dados_json = dados_colunas.to_dict(orient='records')

  return jsonify(dados_json)


@app.route('/api/indicadores', methods=['GET'])
def listar_todos_indicadores():
  json_data = df_indicadores.to_json(orient='records')
  return jsonify(json_data)


@app.route('/api/v1/indicadores/<empresa>', methods=['GET'])
def consultar_indicadores_empresa(empresa):
  # Filtrar os indicadores da empresa desejada no DataFrame "df_indicadores"
  indicadores_empresa = df_indicadores[df_indicadores['Empresa'] == empresa]

  # Verificar se a empresa existe no DataFrame
  if indicadores_empresa.empty:
    return f'Empresa "{empresa}" não encontrada.', 404

  # Converter os indicadores para um formato adequado para o JSON
  indicadores_json = indicadores_empresa.to_dict(orient='records')

  return jsonify(indicadores_json)


@app.route('/api/v1/indicadores', methods=['GET'])
def listar_indicadores():
  # Obter os parâmetros da query string
  empresa = request.args.get('empresa')
  coluna = request.args.get('coluna')

  # Verificar se os parâmetros foram fornecidos
  if empresa is None or coluna is None:
    return 'Parâmetros "empresa" e "coluna" devem ser fornecidos na query string.', 400

  # Filtrar os dados da empresa desejada no DataFrame "df_indicadores"
  dados_empresa = df_indicadores[df_indicadores['Empresa'] == empresa]

  # Verificar se a empresa existe no DataFrame
  if dados_empresa.empty:
    return f'Empresa "{empresa}" não encontrada.', 404

  # Verificar se a coluna existe no DataFrame
  if coluna not in dados_empresa.columns:
    return f'Coluna "{coluna}" não encontrada.', 404

  # Selecionar as colunas desejadas, incluindo a coluna "Data"
  dados_colunas = dados_empresa[['Data', coluna]]

  # Converter os dados para um formato adequado para o JSON
  dados_json = dados_colunas.to_dict(orient='records')

  return jsonify(dados_json)


@app.route('/api/v1/indicadores/<empresa>/<coluna>', methods=['GET'])
def consultar_indicador_empresa(empresa, coluna):
  # Filtrar os indicadores da empresa desejada no DataFrame "df_indicadores"
  indicadores_empresa = df_indicadores[df_indicadores['Empresa'] == empresa]

  # Verificar se a empresa existe no DataFrame
  if indicadores_empresa.empty:
    return f'Empresa "{empresa}" não encontrada.', 404

  # Verificar se a coluna existe no DataFrame
  if coluna not in indicadores_empresa.columns:
    return f'Coluna "{coluna}" não encontrada.', 404

  # Selecionar as colunas desejadas, incluindo a coluna "IBOV"
  dados_colunas = indicadores_empresa[['Data', coluna, 'IBOV']]

  # Converter os dados para um formato adequado para o JSON
  dados_json = dados_colunas.to_dict(orient='records')

  return jsonify(dados_json)


@app.errorhandler(404)
def pagina_nao_encontrada(error):
  return "<h1>A página não existe...</h1>", 404


@app.route('/api/v1/acao/<ticker>', methods=['GET'])
def obter_informacoes_acao(ticker):
  try:
    acao = yf.Ticker(ticker + '.SA')
    informacoes_gerais = acao.info

    # Extraia as informações desejadas do dicionário informacoes_gerais
    preco_atual = informacoes_gerais['currentPrice']
    preco_anterior = informacoes_gerais['previousClose']
    capitalizacao_mercado = informacoes_gerais['marketCap']
    relacao_preco_lucro = informacoes_gerais['trailingPE']

    if 'returnOnEquity' in informacoes_gerais:
      roe = informacoes_gerais['returnOnEquity']
    else:
      roe = None

    if 'priceToBook' in informacoes_gerais:
      p_vpa = informacoes_gerais['priceToBook']
    else:
      p_vpa = None

    if 'bookValue' in informacoes_gerais:
      vpa = informacoes_gerais['bookValue']
    else:
      vpa = None

    # Crie um dicionário com as informações da ação
    informacoes_acao = {
      'ticker': ticker,
      'preco_atual': preco_atual,
      'preco_anterior': preco_anterior,
      'capitalizacao_mercado': capitalizacao_mercado,
      'relacao_preco_lucro': relacao_preco_lucro,
      'roe': roe,
      'p_vpa': p_vpa,
      'vpa': vpa
    }

    return jsonify(informacoes_acao)
  except Exception as e:
    return jsonify({'error': str(e)}), 400


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=81)
