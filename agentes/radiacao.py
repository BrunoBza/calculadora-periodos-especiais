from datetime import datetime
from typing import List, Dict
from .utils import fragmentar_periodo, formatar_resultado

# Datas de corte para o agente radiação
DATAS_CORTE = [
    datetime(1997, 3, 6),  # Data exemplo - ajuste conforme a legislação
]

def avaliar_subperiodo(data_inicio: datetime, data_fim: datetime, tipo_radiacao: str, dose: float) -> bool:
    """
    Avalia se um subperíodo é especial para exposição à radiação.
    
    Args:
        data_inicio: Data de início do período
        data_fim: Data de fim do período
        tipo_radiacao: Tipo de radiação (ionizante, não-ionizante)
        dose: Dose de exposição
    """
    if tipo_radiacao.lower() == 'ionizante':
        return True
    return dose > 0

def avaliar_periodo(data_inicio: datetime, data_fim: datetime, intensidade: float, tipo_radiacao: str = 'ionizante') -> List[Dict]:
    """
    Avalia um período completo para exposição à radiação.
    
    Args:
        data_inicio: Data de início do período
        data_fim: Data de fim do período
        intensidade: Dose de radiação
        tipo_radiacao: Tipo de radiação (ionizante, não-ionizante)
    
    Returns:
        Lista de dicionários contendo informações de cada subperíodo
    """
    subperiodos = fragmentar_periodo(data_inicio, data_fim, DATAS_CORTE)
    resultados = []
    
    for inicio_sub, fim_sub in subperiodos:
        eh_especial = avaliar_subperiodo(inicio_sub, fim_sub, tipo_radiacao, intensidade)
        
        resultados.append(formatar_resultado(
            data_inicio=inicio_sub,
            data_fim=fim_sub,
            agente='radiacao',
            intensidade=intensidade,
            eh_especial=eh_especial,
            unidade='mSv',
            detalhes={'tipo_radiacao': tipo_radiacao}
        ))
    
    return resultados