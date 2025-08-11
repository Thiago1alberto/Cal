"""
Calculadora tributária para comparação entre legislação atual e RTI
"""
from decimal import Decimal
from typing import Dict, List, Any, Tuple
import pandas as pd

from ..models import NotaFiscal, ConfigTributacao, CalculoComparativo, TributoItem


class CalculadoraTributaria:
    """Calculadora para comparação tributária antes e depois da RTI"""
    
    def __init__(self, config_rti: ConfigTributacao = None):
        self.config_rti = config_rti or ConfigTributacao()
        self.cst_data = None
    
    def carregar_tabela_cst(self, df_cst: pd.DataFrame):
        """Carrega tabela de CST com configurações da RTI"""
        self.cst_data = df_cst.copy()
        
        # Padroniza colunas necessárias
        required_cols = ['CST', 'Exige Trib', 'Monofásica', 'Red. Alíq', 'Diferimento', '% Red. CBS', '% Red. IBS']
        
        for col in required_cols:
            if col not in self.cst_data.columns:
                self.cst_data[col] = None
                
        # Converte percentuais para decimais
        for col in ['% Red. CBS', '% Red. IBS']:
            if col in self.cst_data.columns:
                self.cst_data[col] = (self.cst_data[col]
                                     .fillna(0)
                                     .apply(lambda x: Decimal(str(x)) / 100 if x and x != 'nan' else Decimal('0')))
    
    def calcular_tributos_atuais(self, nota_fiscal: NotaFiscal) -> Dict[str, Decimal]:
        """Calcula tributos da legislação atual"""
        totais = {
            'PIS': Decimal('0'),
            'COFINS': Decimal('0'),
            'IPI': Decimal('0'),
            'ICMS': Decimal('0'),
            'ISS': Decimal('0'),
            'TOTAL': Decimal('0')
        }
        
        # Soma tributos diretos do XML
        for item in nota_fiscal.itens:
            for tributo in item.tributos:
                tipo = tributo.tipo.upper()
                if tipo in ['PIS', 'COFINS', 'IPI', 'ICMS']:
                    totais[tipo] += tributo.valor
        
        # Calcula ISS se a flag estiver ativada (5% sobre o total dos outros tributos)
        if self.config_rti.incluir_iss:
            base_iss = totais['PIS'] + totais['COFINS'] + totais['IPI'] + totais['ICMS']
            totais['ISS'] = base_iss * self.config_rti.iss_percentual
        
        # Total = PIS + COFINS + IPI + ICMS + ISS (se aplicável)
        totais['TOTAL'] = totais['PIS'] + totais['COFINS'] + totais['IPI'] + totais['ICMS'] + totais['ISS']
        
        return totais
    
    def calcular_tributos_rti(self, nota_fiscal: NotaFiscal) -> Dict[str, Decimal]:
        """Calcula tributos da nova legislação RTI"""
        if self.cst_data is None:
            raise ValueError("Tabela de CST deve ser carregada primeiro")
        
        total_cbs = Decimal('0')
        total_ibs = Decimal('0')
        
        for item in nota_fiscal.itens:
            # Aplica configuração RTI por item
            cbs_item, ibs_item = self.calcular_rti_item(item)
            total_cbs += cbs_item
            total_ibs += ibs_item
        
        total_rti = total_cbs + total_ibs
        
        return {
            'CBS': total_cbs,
            'IBS': total_ibs,
            'TOTAL': total_rti
        }
    
    def calcular_rti_item(self, item: Any) -> Tuple[Decimal, Decimal]:
        """Calcula CBS e IBS para um item específico"""
        cst = str(item.cst) if hasattr(item, 'cst') else '000'
        valor_item = Decimal(str(item.valor_total or 0))
        
        # Busca configuração na tabela CST
        config_cst = self._buscar_config_cst(cst)
        
        # Calcula alíquotas efetivas
        aliq_cbs = self._calcular_aliquota_efetiva(
            self.config_rti.aliquota_cbs, 
            config_cst.get('% Red. CBS', Decimal('0'))
        )
        aliq_ibs = self._calcular_aliquota_efetiva(
            self.config_rti.aliquota_ibs,
            config_cst.get('% Red. IBS', Decimal('0'))
        )
        
        # Verifica se tributo é exigido
        if not config_cst.get('Exige Trib', True):
            return Decimal('0'), Decimal('0')
        
        cbs = valor_item * aliq_cbs
        ibs = valor_item * aliq_ibs
        
        return cbs, ibs
    
    def _buscar_config_cst(self, cst: str) -> Dict[str, Any]:
        """Busca configuração para um CST específico"""
        if self.cst_data is None:
            return {}
            
        cst_row = self.cst_data[self.cst_data['CST'] == cst]
        
        if not cst_row.empty:
            return cst_row.iloc[0].to_dict()
        
        return {
            'Exige Trib': True,
            'Monofásica': False,
            'Red. Alíq': False,
            'Diferimento': False,
            '% Red. CBS': Decimal('0'),
            '% Red. IBS': Decimal('0')
        }
    
    def _calcular_aliquota_efetiva(self, aliquota_base: Decimal, reducao: Decimal) -> Decimal:
        """Calcula alíquota efetiva considerando reduções"""
        return aliquota_base * (Decimal('1') - reducao)
    
    def realizar_comparacao(self, nota_fiscal: NotaFiscal) -> CalculoComparativo:
        """Realiza comparação completa entre legislação atual e RTI"""
        tributos_atuais = self.calcular_tributos_atuais(nota_fiscal)
        tributos_rti = self.calcular_tributos_rti(nota_fiscal)
        
        # Calcula impacto
        total_atual = tributos_atuais['TOTAL']
        total_novo = tributos_rti['TOTAL']
        economia = total_atual - total_novo
        percentual_economia = (economia / total_atual * 100) if total_atual > 0 else Decimal('0')
        
        return CalculoComparativo(
            tributacao_atual=tributos_atuais,
            tributacao_nova=tributos_rti,
            economia_total=economia,
            percentual_economia=percentual_economia,
            nota_fiscal=nota_fiscal,
            detalhes_atuais=self._gerar_detalhamento_completo(tributos_atuais),
            detalhes_novos=self._gerar_detalhamento_completo(tributos_rti)
        )
    
    def _gerar_detalhamento_completo(self, tributos: Dict[str, Decimal]) -> Dict[str, Any]:
        """Gera detalhamento completo dos tributos calculados"""
        detalhes = {}
        total = tributos['TOTAL']
        
        for tipo, valor in tributos.items():
            if tipo != 'TOTAL':
                detalhes[tipo] = {
                    'valor': valor,
                    'percentual': (valor / total * 100) if total > 0 else Decimal('0'),
                    'descricao': self._get_descricao_tributo(tipo)
                }
        
        return detalhes
    
    def _get_descricao_tributo(self, tipo: str) -> str:
        """Retorna descrição do tributo"""
        descricoes = {
            'PIS': 'Programa de Integração Social',
            'COFINS': 'Contribuição para o Financiamento da Seguridade Social',
            'IPI': 'Imposto sobre Produtos Industrializados',
            'ICMS': 'Imposto sobre Circulação de Mercadorias e Serviços',
            'ISS': 'Imposto sobre Serviços de Qualquer Natureza',
            'CBS': 'Contribuição sobre Bens e Serviços',
            'IBS': 'Imposto sobre Bens e Serviços'
        }
        return descricoes.get(tipo, tipo)
    
    def calcular_item_detalhado(self, item: Any) -> Dict[str, Any]:
        """Calcula tributos de um item com detalhamento completo"""
        resultado = {
            'item_info': {
                'descricao': getattr(item, 'descricao', 'N/A'),
                'ncm': getattr(item, 'ncm', 'N/A'),
                'cst': getattr(item, 'cst', 'N/A'),
                'valor_total': Decimal(str(getattr(item, 'valor_total', 0)))
            },
            'tributos_atuais': {
                'PIS': Decimal('0'),
                'COFINS': Decimal('0'),
                'IPI': Decimal('0'),
                'ICMS': Decimal('0'),
                'ISS': Decimal('0'),
                'TOTAL': Decimal('0')
            },
            'tributos_novos': {
                'CBS': Decimal('0'),
                'IBS': Decimal('0'),
                'TOTAL': Decimal('0')
            }
        }
        
        # Calcula tributos atuais do item
        if hasattr(item, 'tributos'):
            for tributo in item.tributos:
                tipo = tributo.tipo.upper()
                if tipo in ['PIS', 'COFINS', 'IPI', 'ICMS']:
                    resultado['tributos_atuais'][tipo] = tributo.valor
                    resultado['tributos_atuais']['TOTAL'] += tributo.valor
        
        # Adiciona ISS se configurado
        if self.config_rti.incluir_iss:
            base_iss = (resultado['tributos_atuais']['PIS'] + 
                       resultado['tributos_atuais']['COFINS'] + 
                       resultado['tributos_atuais']['IPI'] + 
                       resultado['tributos_atuais']['ICMS'])
            resultado['tributos_atuais']['ISS'] = base_iss * self.config_rti.iss_percentual
            resultado['tributos_atuais']['TOTAL'] += resultado['tributos_atuais']['ISS']
        
        # Calcula tributos RTI do item
        if self.cst_data is not None:
            cbs, ibs = self.calcular_rti_item(item)
            resultado['tributos_novos']['CBS'] = cbs
            resultado['tributos_novos']['IBS'] = ibs
            resultado['tributos_novos']['TOTAL'] = cbs + ibs
        
        # Calcula impacto
        resultado['impacto'] = {
            'economia': resultado['tributos_atuais']['TOTAL'] - resultado['tributos_novos']['TOTAL'],
            'percentual': ((resultado['tributos_atuais']['TOTAL'] - resultado['tributos_novos']['TOTAL']) 
                          / resultado['tributos_atuais']['TOTAL'] * 100) 
                          if resultado['tributos_atuais']['TOTAL'] > 0 else Decimal('0')
        }
        
        return resultado
