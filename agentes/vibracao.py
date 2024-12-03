from datetime import datetime

def avaliar_periodo(data_inicio: datetime, data_fim: datetime, intensidade: float) -> bool:
    """
    Avalia se um período é especial para vibração de corpo inteiro.
    
    Args:
        data_inicio: Data de início do período
        data_fim: Data de fim do período
        intensidade: Nível de vibração em m/s²
    
    Returns:
        bool: True se o período é especial, False caso contrário
    """
    # Implementar critérios específicos para vibração
    return intensidade > 1.1  # Valor de referência conforme normas
