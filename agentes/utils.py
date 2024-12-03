from datetime import datetime, date, timedelta

DATA_FORMAT = "%d/%m/%Y"

def formatar_data(data):
    """Formata uma data para o formato DD/MM/AAAA."""
    if isinstance(data, datetime):
        data = data.date()
    return data.strftime(DATA_FORMAT)

def fragmentar_periodo(data_inicio, data_fim, datas_corte):
    """
    Fragmenta um período em subperíodos baseado nas datas de corte.
    
    Args:
        data_inicio (date): Data de início do período
        data_fim (date): Data de fim do período
        datas_corte (list): Lista de datas que representam mudanças na legislação
    
    Returns:
        list: Lista de tuplas (data_inicio, data_fim)
    """
    # Converte as datas para date se forem datetime
    if isinstance(data_inicio, datetime):
        data_inicio = data_inicio.date()
    if isinstance(data_fim, datetime):
        data_fim = data_fim.date()
    
    # Ordena as datas de corte
    datas_corte = sorted(datas_corte)
    
    # Inicializa a lista de períodos
    periodos = []
    inicio_atual = data_inicio
    
    # Verifica cada data de corte
    for data_corte in datas_corte:
        if isinstance(data_corte, datetime):
            data_corte = data_corte.date()
            
        if inicio_atual < data_corte <= data_fim:
            # Adiciona o período até a data de corte
            periodos.append((inicio_atual, data_corte - timedelta(days=1)))
            inicio_atual = data_corte
    
    # Adiciona o período final
    if inicio_atual <= data_fim:
        periodos.append((inicio_atual, data_fim))
    
    return periodos

def formatar_resultado(data_inicio, data_fim, agente, intensidade, eh_especial, limite=None, unidade="", detalhes=None):
    """
    Formata o resultado da análise de um subperíodo.
    
    Args:
        data_inicio: Data de início do subperíodo
        data_fim: Data de fim do subperíodo
        agente: Nome do agente nocivo
        intensidade: Valor da intensidade
        eh_especial: Se o período é especial ou não
        limite: Valor limite para o período (opcional)
        unidade: Unidade de medida (opcional)
        detalhes: Informações adicionais específicas do agente (opcional)
    
    Returns:
        Dicionário com as informações formatadas do subperíodo
    """
    resultado = {
        'data_inicio': formatar_data(data_inicio),
        'data_fim': formatar_data(data_fim),
        'intensidade': intensidade,
        'eh_especial': eh_especial,
        'unidade': unidade,
        'unidade_limite': unidade  # Adicionando a unidade do limite
    }
    
    if limite is not None:
        resultado['limite'] = limite
        
    if detalhes:
        resultado['detalhes'] = detalhes
        
    return resultado
