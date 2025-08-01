"""
Utilitários para formatação e validação
"""
from decimal import Decimal
from typing import Union, Optional
import re


def format_currency(value: Union[Decimal, float, str], symbol: str = 'R$') -> str:
    """
    Formata valor monetário no padrão brasileiro
    
    Args:
        value: Valor a ser formatado
        symbol: Símbolo da moeda (padrão: R$)
    
    Returns:
        String formatada no padrão brasileiro (R$ 1.234,56)
    """
    try:
        if isinstance(value, str):
            value = Decimal(value)
        elif isinstance(value, float):
            value = Decimal(str(value))
        elif not isinstance(value, Decimal):
            value = Decimal('0')
        
        # Converte para float para formatação
        float_value = float(value)
        
        # Formata com separadores brasileiros
        formatted = f"{float_value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        
        return f"{symbol} {formatted}"
        
    except (ValueError, TypeError, Exception):
        return f"{symbol} 0,00"


def format_percentage(value: Union[Decimal, float, str], decimals: int = 2) -> str:
    """
    Formata valor como porcentagem
    
    Args:
        value: Valor a ser formatado (já como porcentagem, ex: 10.5 para 10.5%)
        decimals: Número de casas decimais
    
    Returns:
        String formatada como porcentagem (10,50%)
    """
    try:
        if isinstance(value, str):
            value = Decimal(value)
        elif isinstance(value, float):
            value = Decimal(str(value))
        elif not isinstance(value, Decimal):
            value = Decimal('0')
        
        float_value = float(value)
        formatted = f"{float_value:.{decimals}f}".replace(".", ",")
        
        return f"{formatted}%"
        
    except (ValueError, TypeError, Exception):
        return "0,00%"


def clean_cnpj_cpf(document: str) -> str:
    """
    Limpa e formata CNPJ/CPF removendo caracteres especiais
    
    Args:
        document: Documento a ser limpo
    
    Returns:
        Documento apenas com números
    """
    if not document:
        return ""
    
    return re.sub(r'[^\d]', '', str(document))


def format_cnpj(cnpj: str) -> str:
    """
    Formata CNPJ no padrão XX.XXX.XXX/XXXX-XX
    
    Args:
        cnpj: CNPJ a ser formatado
    
    Returns:
        CNPJ formatado ou string original se inválida
    """
    cleaned = clean_cnpj_cpf(cnpj)
    
    if len(cleaned) == 14:
        return f"{cleaned[:2]}.{cleaned[2:5]}.{cleaned[5:8]}/{cleaned[8:12]}-{cleaned[12:14]}"
    
    return cnpj


def format_cpf(cpf: str) -> str:
    """
    Formata CPF no padrão XXX.XXX.XXX-XX
    
    Args:
        cpf: CPF a ser formatado
    
    Returns:
        CPF formatado ou string original se inválida
    """
    cleaned = clean_cnpj_cpf(cpf)
    
    if len(cleaned) == 11:
        return f"{cleaned[:3]}.{cleaned[3:6]}.{cleaned[6:9]}-{cleaned[9:11]}"
    
    return cpf


def validate_xml_nfe(xml_content: str) -> tuple[bool, Optional[str]]:
    """
    Valida se o conteúdo XML é uma NF-e válida usando o parser principal
    
    Args:
        xml_content: Conteúdo do XML
    
    Returns:
        Tupla (é_válido, mensagem_erro)
    """
    if not xml_content or not xml_content.strip():
        return False, "Arquivo XML vazio"
    
    # Verifica se é XML válido
    if not xml_content.strip().startswith('<?xml') and not xml_content.strip().startswith('<'):
        return False, "Arquivo não parece ser um XML válido"
    
    # Usa o parser principal para validação mais robusta
    try:
        from src.parser.nf_parser import NFParser
        parser = NFParser()
        is_valid = parser.validate_nf_structure(xml_content)
        
        if not is_valid:
            return False, "Arquivo não é uma NF-e ou NFC-e válida (estrutura não reconhecida)"
        
        return True, None
        
    except Exception as e:
        return False, f"Erro na validação: {str(e)}"


def safe_decimal_conversion(value: any, default: Decimal = Decimal('0')) -> Decimal:
    """
    Converte valor para Decimal de forma segura
    
    Args:
        value: Valor a ser convertido
        default: Valor padrão se conversão falhar
    
    Returns:
        Valor convertido para Decimal
    """
    if value is None:
        return default
    
    try:
        if isinstance(value, Decimal):
            return value
        
        if isinstance(value, str):
            # Remove caracteres não numéricos exceto ponto, vírgula e sinal
            cleaned = re.sub(r'[^\d.,-]', '', value.strip())
            
            if not cleaned:
                return default
            
            # Trata diferentes formatos decimais
            if ',' in cleaned and '.' in cleaned:
                # Formato brasileiro: 1.234,56
                if cleaned.rindex(',') > cleaned.rindex('.'):
                    cleaned = cleaned.replace('.', '').replace(',', '.')
                # Formato americano: 1,234.56
                else:
                    cleaned = cleaned.replace(',', '')
            elif ',' in cleaned:
                # Só vírgula - pode ser decimal brasileiro
                if cleaned.count(',') == 1 and len(cleaned.split(',')[1]) <= 2:
                    cleaned = cleaned.replace(',', '.')
                # Múltiplas vírgulas - separador de milhares
                else:
                    cleaned = cleaned.replace(',', '')
            
            return Decimal(cleaned)
        
        return Decimal(str(value))
        
    except (ValueError, TypeError, Exception):
        return default


def get_economy_message(economia_total: Decimal, economia_percentual: Decimal) -> str:
    """
    Gera mensagem amigável sobre economia/aumento de tributos
    
    Args:
        economia_total: Valor da economia (negativo = economia, positivo = aumento)
        economia_percentual: Percentual da economia
    
    Returns:
        Mensagem formatada
    """
    valor_abs = abs(economia_total)
    percentual_abs = abs(economia_percentual)
    
    if economia_total < 0:
        # Economia (redução de tributos)
        return f"🎉 **ECONOMIA de {format_currency(valor_abs)}** ({format_percentage(percentual_abs)})"
    elif economia_total > 0:
        # Aumento de tributos
        return f"⚠️ **AUMENTO de {format_currency(valor_abs)}** ({format_percentage(percentual_abs)})"
    else:
        # Sem alteração
        return "➡️ **SEM ALTERAÇÃO** na carga tributária"


def generate_summary_stats(detalhes: list) -> dict:
    """
    Gera estatísticas resumidas dos cálculos
    
    Args:
        detalhes: Lista de detalhes por item
    
    Returns:
        Dicionário com estatísticas
    """
    if not detalhes:
        return {
            'total_itens': 0,
            'itens_com_economia': 0,
            'itens_com_aumento': 0,
            'itens_sem_alteracao': 0,
            'maior_economia': 0,
            'maior_aumento': 0
        }
    
    economias = [d['diferenca'] for d in detalhes if d['diferenca'] < 0]
    aumentos = [d['diferenca'] for d in detalhes if d['diferenca'] > 0]
    sem_alteracao = [d for d in detalhes if d['diferenca'] == 0]
    
    return {
        'total_itens': len(detalhes),
        'itens_com_economia': len(economias),
        'itens_com_aumento': len(aumentos),
        'itens_sem_alteracao': len(sem_alteracao),
        'maior_economia': abs(min(economias)) if economias else 0,
        'maior_aumento': max(aumentos) if aumentos else 0
    }
