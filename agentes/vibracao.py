from datetime import datetime
from typing import Tuple, List, Dict
from .utils import fragmentar_periodo, formatar_data

def get_unidade_e_limite(data_fim: datetime, unidade_informada: str = None) -> Tuple[str, float, str]:
    """
    Determina a unidade de medida e limite corretos para um determinado período.
    
    Args:
        data_fim: Data fim do período
        unidade_informada: Unidade informada pelo usuário (opcional)
    
    Returns:
        Tuple[str, float, str]: (unidade correta, limite, unidade formatada)
    """
    data_fim = data_fim.date() if isinstance(data_fim, datetime) else data_fim
    
    # Definição dos limites e unidades por período
    limites = {
        'gpm': 120,
        'ms2': {'1997': 0.86, '2014': 1.1},
        'ms175': 21.0
    }

    unidades_texto = {
        'gpm': 'golpes por minuto',
        'ms2': 'm/s² (aren)',
        'ms175': 'm/s1,75(VDVR)'
    }

    # Determina a unidade correta para o período
    if data_fim < datetime(1997, 3, 6).date():
        unidade_correta = 'gpm'
        limite = limites['gpm']
    elif data_fim < datetime(2014, 8, 13).date():
        unidade_correta = 'ms2'
        limite = limites['ms2']['1997']
    else:
        if unidade_informada == 'ms175':
            unidade_correta = 'ms175'
            limite = limites['ms175']
        else:
            unidade_correta = 'ms2'
            limite = limites['ms2']['2014']
    
    return unidade_correta, limite, unidades_texto[unidade_correta]

def avaliar_periodo(data_inicio: datetime, data_fim: datetime, intensidade: float, unidade: str) -> Tuple[bool, str, Dict]:
    """
    Avalia se um período é especial para vibração de corpo inteiro.
    
    Args:
        data_inicio: Data de início do período
        data_fim: Data de fim do período
        intensidade: Nível de vibração
        unidade: Unidade de medida ('gpm' para golpes por minuto, 'ms2' para m/s², 'ms175' para m/s1.75)
    
    Returns:
        Tuple[bool, str, Dict]: (True se o período é especial, mensagem explicativa, dados adicionais)
    """
    # Convertendo para date para comparação
    data_marco_1997 = datetime(1997, 3, 6).date()
    data_agosto_2014 = datetime(2014, 8, 13).date()
    data_inicio = data_inicio.date() if isinstance(data_inicio, datetime) else data_inicio
    data_fim = data_fim.date() if isinstance(data_fim, datetime) else data_fim
    
    # Definição dos limites por unidade
    limites = {
        'gpm': 120,  # golpes por minuto
        'ms2': 0.86 if data_fim < data_agosto_2014 else 1.1,  # m/s² (aren)
        'ms175': 21.0  # m/s1,75 (VDVR)
    }
    
    unidades_texto = {
        'gpm': 'golpes por minuto',
        'ms2': 'm/s² (aren)',
        'ms175': 'm/s1,75(VDVR)'
    }

    # Prepara os dados básicos
    unidade_texto = unidades_texto.get(unidade, unidade)
    dados = {
        'intensidade': intensidade,
        'unidade': unidade_texto
    }

    # Determina a unidade correta, limite e fundamento legal para o período
    if data_fim < data_marco_1997:
        unidade_correta = 'gpm'
        limite_correto = limites['gpm']
        fundamento = 'Anexo do Decreto nº 53.831/1964, código 1.1.5'
    elif data_fim < data_agosto_2014:
        unidade_correta = 'ms2'
        limite_correto = limites['ms2']
        fundamento = 'Decreto nº 2.172/1997 e norma ISO 2631/1997'
    else:
        if unidade == 'ms175':
            unidade_correta = 'ms175'
            limite_correto = limites['ms175']
        else:
            unidade_correta = 'ms2'
            limite_correto = limites['ms2']
        fundamento = 'Anexo 8, da NR-15, com as alterações da Portaria MTE nº 1.297/2014'

    # Sempre usa a unidade correta para o limite
    dados['limite'] = limite_correto
    dados['unidade_limite'] = unidades_texto[unidade_correta]  # Unidade específica para o limite
    dados['fundamento'] = fundamento

    # Verifica se a unidade está correta para o período
    if unidade != unidade_correta:
        # Caso especial para período após 2014 onde são aceitas duas unidades
        if data_fim >= datetime(2014, 8, 13).date() and unidade == 'gpm':
            mensagem = (
                f"O período de {formatar_data(data_inicio)} a {formatar_data(data_fim)} não deve ser enquadrado como especial, "
                f"em razão da utilização de metodologia inapropriada. Para este período (de {formatar_data(data_inicio)} a {formatar_data(data_fim)}), "
                f"a unidade de medida deve ser 'm/s² (aren)' ou 'm/s1,75(VDVR)', enquanto as provas produzidas "
                f"informam o valor em {unidade_texto}, o que não se enquadra no {fundamento}"
            )
        else:
            mensagem = (
                f"O período de {formatar_data(data_inicio)} a {formatar_data(data_fim)} não deve ser enquadrado como especial, "
                f"em razão da utilização de metodologia inapropriada. Para este período (de {formatar_data(data_inicio)} a {formatar_data(data_fim)}), "
                f"a unidade de medida deve ser '{unidades_texto[unidade_correta]}', enquanto as provas produzidas "
                f"informam o valor em {unidade_texto}, o que não se enquadra no {fundamento}"
            )
        dados['mensagem_unidade_inadequada'] = True
        dados['mensagem_completa'] = mensagem
        return False, mensagem, dados

    # Se chegou aqui, a unidade está correta
    eh_especial = intensidade > limite_correto
    if eh_especial:
        mensagem = (
            f"em razão de a intensidade informada de {intensidade} {unidade_texto} superar "
            f"o limite de {limite_correto} {unidades_texto[unidade_correta]}, previsto no {fundamento}"
        )
    else:
        mensagem = (
            f"em razão de a intensidade informada de {intensidade} {unidade_texto} não superar "
            f"o limite de {limite_correto} {unidades_texto[unidade_correta]}, previsto no {fundamento}"
        )
    
    return eh_especial, mensagem, dados

def processar_periodo(data_inicio: datetime, data_fim: datetime, intensidade: float, unidade: str = None) -> List[Dict]:
    """
    Processa um período de exposição à vibração, fragmentando-o conforme as datas de corte.
    
    Args:
        data_inicio: Data de início do período
        data_fim: Data de fim do período
        intensidade: Nível de vibração
        unidade: Unidade de medida ('gpm', 'ms2' ou 'ms175')
    
    Returns:
        List[Dict]: Lista de subperíodos com suas respectivas avaliações
    """
    # Datas de corte para vibração
    datas_corte = [
        datetime(1997, 3, 6),  # Mudança de critério: golpes/min para m/s²
        datetime(2014, 8, 13)  # Mudança de critério: inclusão de m/s1.75
    ]
    
    # Fragmenta o período
    subperiodos = fragmentar_periodo(data_inicio, data_fim, datas_corte)
    resultados = []
    
    for inicio_sub, fim_sub in subperiodos:
        eh_especial, mensagem, dados = avaliar_periodo(inicio_sub, fim_sub, intensidade, unidade)
        
        resultados.append({
            'data_inicio': formatar_data(inicio_sub),
            'data_fim': formatar_data(fim_sub),
            'eh_especial': eh_especial,
            'mensagem': mensagem,
            'limite': dados.get('limite', ''),
            'unidade': dados.get('unidade', ''),
            'intensidade': dados.get('intensidade', ''),
            'unidade_limite': dados.get('unidade_limite', ''),  # Adicionando a unidade do limite
            'fundamento': dados.get('fundamento', '')  # Adicionando o fundamento legal
        })
    
    return resultados
