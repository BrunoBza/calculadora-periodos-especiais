from datetime import datetime
from typing import List, Dict
from .utils import fragmentar_periodo, formatar_resultado

# Datas de corte para o agente eletricidade
DATAS_CORTE = [
    datetime(1997, 3, 6),  # Data exemplo - ajuste conforme a legislação
]

def obter_limite(data: datetime) -> float:
    """Retorna o limite de tensão elétrica para a data especificada."""
    return 250.0  # Valor exemplo - ajuste conforme a legislação

def avaliar_subperiodo(data_inicio: datetime, data_fim: datetime, tensao: float) -> bool:
    """Avalia se um subperíodo é especial para exposição à eletricidade."""
    limite = obter_limite(data_inicio)
    return tensao > limite

def avaliar_periodo(data_inicio: datetime, data_fim: datetime, intensidade: float) -> List[Dict]:
    """
    Avalia um período completo para exposição à eletricidade.
    
    Args:
        data_inicio: Data de início do período
        data_fim: Data de fim do período
        intensidade: Tensão elétrica em volts
    
    Returns:
        Lista de dicionários contendo informações de cada subperíodo
    """
    subperiodos = fragmentar_periodo(data_inicio, data_fim, DATAS_CORTE)
    resultados = []
    
    for inicio_sub, fim_sub in subperiodos:
        limite = obter_limite(inicio_sub)
        eh_especial = avaliar_subperiodo(inicio_sub, fim_sub, intensidade)
        
        resultados.append(formatar_resultado(
            data_inicio=inicio_sub,
            data_fim=fim_sub,
            agente='eletricidade',
            intensidade=intensidade,
            eh_especial=eh_especial,
            limite=limite,
            unidade='V'
        ))
    
    return resultados
