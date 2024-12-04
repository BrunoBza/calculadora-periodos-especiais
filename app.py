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
    },
    'vibracao': {
        'ate_1997': 'Anexo do Decreto nº 53.831/1964, código 1.1.5',
        'de_1997_a_2014': 'Decreto nº 2.172/1997 e norma ISO 2631/1997',
        'apos_2014': 'Anexo 8, da NR-15, com as alterações da Portaria MTE nº 1.297/2014'
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
                    data_inicio = datetime.strptime(periodo['data_inicio'], DATA_FORMAT)
                    data_fim = datetime.strptime(periodo['data_fim'], DATA_FORMAT)
                except ValueError:
                    raise ValueError("Formato de data inválido. Use DD/MM/AAAA")
                
                if data_fim.date() < data_inicio.date():
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
                
                # Validação da unidade de medida para vibração
                if periodo['agente'] == 'vibracao':
                    if 'unidade_medida' not in periodo:
                        raise ValueError("Unidade de medida é obrigatória para vibração")
                    if periodo['unidade_medida'] not in ['gpm', 'ms2', 'ms175']:
                        raise ValueError("Unidade de medida inválida para vibração")
                    
                    # Processa o período com o módulo de vibração incluindo a unidade
                    subperiodos = agente.processar_periodo(
                        data_inicio,
                        data_fim,
                        intensidade,
                        periodo['unidade_medida']
                    )
                else:
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

    minuta = []

    # 1. Períodos em discussão
    periodos = list(periodos_agrupados.values())
    if len(periodos) == 1:
        periodo = periodos[0]
        if periodo['agente'] == 'vibracao':
            texto = (
                f"No caso concreto, é controvertido quanto ao agente nocivo vibração "
                f"o período de {periodo['data_inicio']} a {periodo['data_fim']}, "
                f"com exposição à vibração com intensidade informada de {periodo['intensidade']} "
                f"{resultados[0]['subperiodo'].get('unidade', '')}."
            )
        else:
            texto = (
                f"No caso concreto, é controvertido quanto ao agente nocivo "
                f"{periodo['agente'].replace('_', ' ')} o período de "
                f"{periodo['data_inicio']} a {periodo['data_fim']}, com "
                f"exposição a um nível de {periodo['intensidade']} "
                f"{resultados[0]['subperiodo'].get('unidade', '')}."
            )
        minuta.append(texto)
        minuta.append("")
    else:
        minuta.append("No caso concreto, são controvertidos os seguintes períodos:")
        minuta.append("")
        for i, periodo in enumerate(periodos):
            if periodo['agente'] == 'vibracao':
                unidades = {
                    'gpm': 'golpes por minuto',
                    'ms2': 'm/s² (aren)',
                    'ms175': 'm/s1,75(VDVR)'
                }
                texto = (
                    f"De {periodo['data_inicio']} a {periodo['data_fim']}, "
                    f"em razão do agente nocivo vibração, "
                    f"com exposição a uma intensidade informada de {periodo['intensidade']} "
                    f"{unidades[periodo['unidade_medida']]}"
                )
            else:
                texto = (
                    f"De {periodo['data_inicio']} a {periodo['data_fim']}, "
                    f"em razão do agente nocivo {periodo['agente'].replace('_', ' ')}, "
                    f"com exposição a um nível de {periodo['intensidade']} "
                    f"{resultados[0]['subperiodo'].get('unidade', '')}"
                )
            minuta.append(texto + ("." if i == len(periodos) - 1 else ";"))
        minuta.append("")
    # 2. Análise dos subperíodos
    # Ordena todos os subperíodos cronologicamente
    todos_subperiodos = []
    for resultado in resultados:
        subperiodo = resultado['subperiodo']
        periodo_original = resultado['periodo_original']
        agente = periodo_original['agente']
        intensidade = periodo_original['intensidade']
        
        data_inicio = datetime.strptime(subperiodo['data_inicio'], DATA_FORMAT)
        todos_subperiodos.append({
            'data_inicio': data_inicio,
            'subperiodo': subperiodo,
            'periodo_original': periodo_original
        })
    
    # Ordena os subperíodos por data de início
    todos_subperiodos.sort(key=lambda x: x['data_inicio'])
    
    # Processa cada subperíodo na ordem cronológica
    for item in todos_subperiodos:
        subperiodo = item['subperiodo']
        periodo_original = item['periodo_original']
        agente = periodo_original['agente']
        intensidade = periodo_original['intensidade']
        
        if agente == 'vibracao':
            if not subperiodo['eh_especial']:
                # Verifica se é caso de unidade inadequada
                if subperiodo.get('mensagem_unidade_inadequada', False):
                    texto = f"{subperiodo['mensagem']}."
                else:
                    texto = (
                        f"O período de {subperiodo['data_inicio']} a {subperiodo['data_fim']} "
                        f"não deve ser enquadrado como especial, {subperiodo['mensagem']}."
                    )
            else:
                texto = (
                    f"O período de {subperiodo['data_inicio']} a {subperiodo['data_fim']} "
                    f"deve ser enquadrado como especial, {subperiodo['mensagem']}."
                )
        else:
            if subperiodo['eh_especial']:
                texto = (
                    f"O período de {subperiodo['data_inicio']} a {subperiodo['data_fim']} "
                    f"deve ser enquadrado como especial, em razão de exposição a {agente.replace('_', ' ')} de "
                    f"{intensidade} {subperiodo['unidade']}, superior ao limite de "
                    f"{subperiodo['limite']}{subperiodo['unidade']} previsto no "
                    f"{subperiodo['fundamento']}."
                )
            else:
                texto = (
                    f"O período de {subperiodo['data_inicio']} a {subperiodo['data_fim']} "
                    f"não deve ser enquadrado como especial, por não ultrapassar o limite de "
                    f"{subperiodo['limite']}{subperiodo['unidade']}, previsto no {subperiodo['fundamento']}."
                )
        
        minuta.append(texto)
        minuta.append("")  # Adiciona uma linha em branco após cada análise de subperíodo

    # 3. Conclusão
    periodos_especiais = []
    for resultado in resultados:
        if resultado['subperiodo']['eh_especial']:
            periodo = resultado['subperiodo']
            periodos_especiais.append(
                f"{periodo['data_inicio']} a {periodo['data_fim']}"
            )

    if periodos_especiais:
        if len(periodos_especiais) == 1:
            minuta.append(
                f"Dessa forma, reconheço como especial o período de "
                f"{periodos_especiais[0]}."
            )
        else:
            minuta.append(
                f"Dessa forma, reconheço como especiais os períodos de "
                f"{', e '.join(periodos_especiais)}."
            )
    else:
        minuta.append("Dessa forma, não reconheço nenhum período como especial.")

    return "\n".join(minuta)

if __name__ == '__main__':
    app.run(debug=True)
