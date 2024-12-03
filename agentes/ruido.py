from datetime import datetime
from typing import List, Dict
from .utils import fragmentar_periodo, formatar_resultado

# Datas de corte para o agente ruído
DATAS_CORTE = [
    datetime(1997, 3, 6),   # Mudança do limite de 80 dB(A) para 90 dB(A)
    datetime(2003, 11, 19), # Mudança do limite de 90 dB(A) para 85 dB(A)
]

def obter_limite(data: datetime) -> float:
    """Retorna o limite de ruído para a data especificada."""
    if isinstance(data, datetime):
        data = data.date()
        
    if data < DATAS_CORTE[0].date():
        return 80.0
    elif data < DATAS_CORTE[1].date():
        return 90.0
    return 85.0

def processar_periodo(data_inicio: datetime, data_fim: datetime, intensidade: float) -> List[Dict]:
    """
    Processa um período completo, fragmentando-o conforme as datas de corte.
    
    Args:
        data_inicio: Data de início do período
        data_fim: Data de fim do período
        intensidade: Nível de ruído em dB(A)
    
    Returns:
        Lista de dicionários contendo informações de cada subperíodo
    """
    subperiodos = fragmentar_periodo(data_inicio, data_fim, DATAS_CORTE)
    resultados = []
    
    for inicio_sub, fim_sub in subperiodos:
        limite = obter_limite(inicio_sub)
        eh_especial = intensidade > limite
        
        resultados.append(formatar_resultado(
            data_inicio=inicio_sub,
            data_fim=fim_sub,
            agente='ruido',
            intensidade=intensidade,
            eh_especial=eh_especial,
            limite=limite,
            unidade='dB(A)'
        ))
    
    return resultados
