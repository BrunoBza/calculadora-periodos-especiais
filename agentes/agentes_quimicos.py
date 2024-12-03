from datetime import datetime
from typing import List

def avaliar_periodo(data_inicio: datetime, data_fim: datetime, agentes: List[str], intensidade: float) -> bool:
    """
    Avalia se um período é especial para agentes químicos.
    
    Args:
        data_inicio: Data de início do período
        data_fim: Data de fim do período
        agentes: Lista de agentes químicos presentes
        intensidade: Concentração ou nível de exposição
    
    Returns:
        bool: True se o período é especial, False caso contrário
    """
    # Implementar lógica específica para cada agente químico
    # Por enquanto, retorna True se houver qualquer exposição
    return len(agentes) > 0
