from flask import Flask, render_template, request, jsonify
from datetime import datetime
from agentes import ruido, agentes_quimicos, vibracao, calor, radiacao, eletricidade
from agentes.utils import DATA_FORMAT, formatar_data
from itertools import groupby
from operator import itemgetter
import os

app = Flask(__name__, 
    static_url_path='',
    static_folder='static',
    template_folder='templates'
)

AGENTES = {
    'ruido': ruido,
    'agentes_quimicos': agentes_quimicos,
    'vibracao': vibracao,
    'calor': calor,
    'radiacao': radiacao,
    'eletricidade': eletricidade
}

# Dicionário com os fundamentos legais para cada agente e época
FUNDAMENTOS_LEGAIS = {
    'ruido': {
        '80': 'Decreto nº 53.831/64',
        '90': 'Decreto nº 2.172/97',
        '85': 'Decreto nº 4.882/2003'
    }
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/avaliar', methods=['POST'])
def avaliar():
    try:
        data = request.get_json()
        if not data or 'periodos' not in data:
            return jsonify({'error': 'Dados inválidos'}), 400
            
        periodos = data['periodos']
        if not periodos:
            return jsonify({'error': 'Nenhum período fornecido'}), 400
        
        resultados = []
        for periodo in periodos:
            try:
                # Validação dos campos obrigatórios
                campos_obrigatorios = ['data_inicio', 'data_fim', 'agente', 'intensidade']
                for campo in campos_obrigatorios:
                    if campo not in periodo:
                        raise ValueError(f"Campo obrigatório ausente: {campo}")
                
                # Conversão e validação das datas
                try:
                    data_inicio = datetime.strptime(periodo['data_inicio'], DATA_FORMAT).date()
                    data_fim = datetime.strptime(periodo['data_fim'], DATA_FORMAT).date()
                except ValueError:
                    raise ValueError("Formato de data inválido. Use DD/MM/AAAA")
                
                if data_fim < data_inicio:
                    raise ValueError("Data fim não pode ser anterior à data início")
                
                # Validação do agente
                agente = AGENTES.get(periodo['agente'])
                if not agente:
                    raise ValueError(f"Agente não encontrado: {periodo['agente']}")
                
                # Conversão e validação da intensidade
                try:
                    intensidade = float(periodo['intensidade'])
                    if intensidade <= 0:
                        raise ValueError("Intensidade deve ser maior que zero")
                except ValueError:
                    raise ValueError("Intensidade inválida")
                
                # Processa o período com o módulo do agente específico
                subperiodos = agente.processar_periodo(data_inicio, data_fim, intensidade)
                
                # Adiciona cada subperíodo como um resultado separado
                for subperiodo in subperiodos:
                    resultados.append({
                        'periodo_original': periodo,
                        'subperiodo': subperiodo
                    })
                
            except Exception as e:
                return jsonify({'error': f"Erro ao processar período: {str(e)}"}), 400
        
        # Gera a minuta com os resultados
        minuta = gerar_minuta(resultados)
        
        return jsonify({
            'resultados': resultados,
            'minuta': minuta
        })
        
    except Exception as e:
        return jsonify({'error': f"Erro interno: {str(e)}"}), 500

def gerar_minuta(resultados):
    # Agrupa os resultados por período original
    periodos_agrupados = {}
    for resultado in resultados:
        periodo = resultado['periodo_original']
        chave = (
            periodo['data_inicio'],
            periodo['data_fim'],
            periodo['agente']
        )
        if chave not in periodos_agrupados:
            periodos_agrupados[chave] = periodo

    # Dicionário com os códigos dos anexos
    codigos_anexos = {
        'ruido': {
            '80': {
                'codigo': '1.1.6',
                'anexo': 'Anexo do Decreto Federal nº 53.831/1964'
            },
            '90': {
                'codigo': '2.0.1',
                'anexo': 'Anexo IV do Decreto Federal nº 2.172/1997 e ' +
                        'Decreto nº 3.048/1999 (redação original)'
            },
            '85': {
                'codigo': '2.0.1',
                'anexo': 'Anexo IV do Decreto Federal nº 3.048/1999, com ' +
                        'redação dada pelo Decreto Federal nº 4.882/2003'
            }
        }
    }

    minuta = []

    # 1. Períodos em discussão
    periodos = list(periodos_agrupados.values())
    if len(periodos) == 1:
        periodo = periodos[0]
        texto = (
            f"No caso concreto, é controvertido quanto ao agente nocivo "
            f"{periodo['agente'].replace('_', ' ')} o período de "
            f"{periodo['data_inicio']} a {periodo['data_fim']}, com "
            f"exposição a um nível de {periodo['intensidade']} "
            f"{resultados[0]['subperiodo']['unidade']}."
        )
        minuta.append(texto)
        minuta.append("")
    else:
        minuta.append(
            f"No caso concreto, são controvertidos quanto ao agente nocivo "
            f"{periodos[0]['agente'].replace('_', ' ')} os seguintes períodos:"
        )
        minuta.append("")
        for i, periodo in enumerate(periodos):
            texto = (
                f"De {periodo['data_inicio']} a {periodo['data_fim']}, "
                f"com exposição a um nível de {periodo['intensidade']} "
                f"{resultados[0]['subperiodo']['unidade']}"
            )
            minuta.append(texto + ("." if i == len(periodos) - 1 else "; e"))
        minuta.append("")

    # 2. Análise dos subperíodos
    # Primeiro os períodos especiais
    periodos_especiais = [r for r in resultados if r['subperiodo']['eh_especial']]
    for resultado in periodos_especiais:
        subperiodo = resultado['subperiodo']
        agente = resultado['periodo_original']['agente']
        intensidade = resultado['periodo_original']['intensidade']
        
        info_anexo = codigos_anexos.get(agente, {}).get(
            str(int(subperiodo['limite'])), {}
        )
        codigo = info_anexo.get('codigo', '')
        anexo = info_anexo.get('anexo', '')
        
        texto = (
            f"O período de {subperiodo['data_inicio']} a "
            f"{subperiodo['data_fim']} deve ser enquadrado como especial, "
            f"em razão de exposição a {agente.replace('_', ' ')} de "
            f"{intensidade} {subperiodo['unidade']}, superior ao limite de "
            f"{subperiodo['limite']}{subperiodo['unidade']} previsto no "
            f"código {codigo}, do {anexo}."
        )
        minuta.append(texto)
        minuta.append("")

    # Depois os períodos não especiais
    periodos_nao_especiais = [r for r in resultados if not r['subperiodo']['eh_especial']]
    for resultado in periodos_nao_especiais:
        subperiodo = resultado['subperiodo']
        agente = resultado['periodo_original']['agente']
        
        info_anexo = codigos_anexos.get(agente, {}).get(
            str(int(subperiodo['limite'])), {}
        )
        codigo = info_anexo.get('codigo', '')
        anexo = info_anexo.get('anexo', '')
        
        texto = (
            f"O período de {subperiodo['data_inicio']} a "
            f"{subperiodo['data_fim']} não deve ser enquadrado como "
            f"especial, por não ultrapassar o limite de "
            f"{subperiodo['limite']}{subperiodo['unidade']}, previsto no "
            f"código {codigo}, do {anexo}."
        )
        minuta.append(texto)
        minuta.append("")

    # 3. Conclusão
    if not periodos_especiais:
        minuta.append("Dessa forma, não reconheço nenhum período como especial.")
        minuta.append("")
    else:
        periodos_texto = []
        for i, resultado in enumerate(periodos_especiais):
            subperiodo = resultado['subperiodo']
            if i == len(periodos_especiais) - 1 and i > 0:
                periodos_texto.append(
                    f"e de {subperiodo['data_inicio']} a "
                    f"{subperiodo['data_fim']}"
                )
            else:
                periodos_texto.append(
                    f"de {subperiodo['data_inicio']} a "
                    f"{subperiodo['data_fim']}"
                )
        
        texto = (
            f"Dessa forma, reconheço como "
            f"{'especial o período' if len(periodos_especiais) == 1 else 'especiais os períodos'} "
            f"{', '.join(periodos_texto)}."
        )
        minuta.append(texto)
        minuta.append("")

    return "\n".join(minuta)

if __name__ == '__main__':
    app.run(debug=True)
