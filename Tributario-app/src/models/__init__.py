"""
Modelos de dados para o sistema tributário
"""
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from decimal import Decimal
import pandas as pd


@dataclass
class TributoItem:
    """Representa um tributo específico de um item da NF-e"""
    tipo: str  # PIS, COFINS, IPI, ICMS, etc.
    cst: str
    base_calculo: Decimal
    aliquota: Decimal
    valor: Decimal


@dataclass
class ItemNF:
    """Representa um item da Nota Fiscal"""
    numero: int
    descricao: str
    ncm: str
    cfop: str
    unidade: str
    quantidade: Decimal
    valor_unitario: Decimal
    valor_total: Decimal
    tributos: List[TributoItem]
    
    def get_tributo(self, tipo: str) -> Optional[TributoItem]:
        """Busca um tributo específico do item"""
        for tributo in self.tributos:
            if tributo.tipo.upper() == tipo.upper():
                return tributo
        return None


@dataclass
class NotaFiscal:
    """Representa uma Nota Fiscal completa"""
    numero: str
    serie: str
    data_emissao: str
    chave_acesso: str
    cnpj_emitente: str
    razao_social_emitente: str
    cnpj_destinatario: str
    razao_social_destinatario: str
    valor_total_produtos: Decimal
    valor_total_nota: Decimal
    itens: List[ItemNF]
    
    def get_total_tributo(self, tipo: str) -> Decimal:
        """Calcula o total de um tipo de tributo na nota"""
        total = Decimal('0')
        for item in self.itens:
            tributo = item.get_tributo(tipo)
            if tributo:
                total += tributo.valor
        return total


@dataclass
class ConfigTributacao:
    """Configuração da nova tributação (RTI)"""
    cbs_aliquota: Decimal = Decimal('0.009')  # 0.9%
    ibs_aliquota: Decimal = Decimal('0.26')   # 26%
    incluir_iss: bool = False  # Flag para incluir ISS no cálculo
    iss_percentual: Decimal = Decimal('0.05')  # 5% sobre o total já somado
    cst_reducoes: Optional[Dict[str, Dict[str, Decimal]]] = None
    
    def __post_init__(self):
        if self.cst_reducoes is None:
            self.cst_reducoes = {}


@dataclass
class CalculoComparativo:
    """Resultado da comparação tributária"""
    nota_fiscal: NotaFiscal
    tributacao_atual: Dict[str, Decimal]
    tributacao_nova: Dict[str, Decimal]
    economia_total: Decimal
    economia_percentual: Decimal
    detalhes_por_item: List[Dict[str, Any]]
