from datetime import datetime

def avaliar_periodo(data_inicio: datetime, data_fim: datetime, ibutg: float) -> bool:
    """
    Avalia se um período é especial para exposição ao calor.
    
    Args:
        data_inicio: Data de início do período
        data_fim: Data de fim do período
        ibutg: Índice de Bulbo Úmido Termômetro de Globo
    
    Returns:
        bool: True se o período é especial, False caso contrário
    """
    # Implementar critérios baseados no IBUTG
    return ibutg > 25.0  # Valor de referência base
