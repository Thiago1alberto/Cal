"""
Calculadora tributária para comparação entre legislação atual e RTI
"""
from decimal import Decimal
from typing import Dict, List, Any
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
                if col == '% Red. CBS':
                    self.cst_data[col] = 0.0
                elif col == '% Red. IBS':
                    self.cst_data[col] = 0.0
                else:
                    self.cst_data[col] = False
        
        # Converte CST para string padronizada
        self.cst_data['CST'] = self.cst_data['CST'].astype(str).str.strip()
        
        # Converte porcentagens para decimais
        for col in ['% Red. CBS', '% Red. IBS']:
            if self.cst_data[col].dtype == 'object':
                # Remove % e converte
                self.cst_data[col] = (self.cst_data[col]
                                     .astype(str)
                                     .str.replace('%', '')
                                     .str.replace(',', '.')
                                     .apply(lambda x: Decimal(x) / 100 if x and x != 'nan' else Decimal('0')))
            else:
                self.cst_data[col] = self.cst_data[col].apply(lambda x: Decimal(str(x)) / 100 if x > 1 else Decimal(str(x)))
    
    def get_cst_config(self, cst: str) -> Dict[str, Any]:
        """Busca configuração de um CST específico"""
        if self.cst_data is None:
            return {
                'exige_trib': True,
                'monofasica': False,
                'red_aliq': False,
                'diferimento': False,
                'reducao_cbs': Decimal('0'),
                'reducao_ibs': Decimal('0')
            }
        
        cst_clean = str(cst).strip()
        
        # Busca exata
        row = self.cst_data[self.cst_data['CST'] == cst_clean]
        
        if row.empty:
            # Busca sem zeros à esquerda
            cst_no_leading_zeros = cst_clean.lstrip('0')
            row = self.cst_data[self.cst_data['CST'].str.lstrip('0') == cst_no_leading_zeros]
        
        if row.empty:
            # CST não encontrado, usa configuração padrão
            return {
                'exige_trib': True,
                'monofasica': False,
                'red_aliq': False,
                'diferimento': False,
                'reducao_cbs': Decimal('0'),
                'reducao_ibs': Decimal('0')
            }
        
        row = row.iloc[0]
        
        return {
            'exige_trib': bool(row.get('Exige Trib', True)),
            'monofasica': bool(row.get('Monofásica', False)),
            'red_aliq': bool(row.get('Red. Alíq', False)),
            'diferimento': bool(row.get('Diferimento', False)),
            'reducao_cbs': Decimal(str(row.get('% Red. CBS', 0))),
            'reducao_ibs': Decimal(str(row.get('% Red. IBS', 0)))
        }
    
    def calcular_tributos_atuais(self, nota_fiscal: NotaFiscal) -> Dict[str, Decimal]:
        """Calcula totais dos tributos atuais da nota fiscal"""
        totais = {
            'PIS': Decimal('0'),
            'COFINS': Decimal('0'),
            'IPI': Decimal('0'),
            'ICMS': Decimal('0'),
            'TOTAL': Decimal('0')
        }
        
        for item in nota_fiscal.itens:
            for tributo in item.tributos:
                tipo = tributo.tipo.upper()
                if tipo in totais:
                    totais[tipo] += tributo.valor
                    totais['TOTAL'] += tributo.valor
        
        return totais
    
    def calcular_tributos_rti(self, nota_fiscal: NotaFiscal) -> Dict[str, Decimal]:
        """Calcula tributos conforme nova RTI (CBS + IBS)"""
        totais = {
            'CBS': Decimal('0'),
            'IBS': Decimal('0'),
            'TOTAL': Decimal('0')
        }
        
        for item in nota_fiscal.itens:
            # Base de cálculo é o valor do produto
            base_calculo = item.valor_total
            
            # Busca configuração CST mais relevante
            cst_configs = []
            for tributo in item.tributos:
                if tributo.cst:
                    config = self.get_cst_config(tributo.cst)
                    cst_configs.append(config)
            
            # Se não tem tributos ou CST, usa configuração padrão
            if not cst_configs:
                cst_config = self.get_cst_config('')
            else:
                # Usa a configuração mais restritiva (que gera menos tributo)
                cst_config = min(cst_configs, key=lambda x: (x['exige_trib'], -x['reducao_cbs'], -x['reducao_ibs']))
            
            # Calcula CBS
            if cst_config['exige_trib'] and not cst_config['monofasica']:
                fator_reducao_cbs = Decimal('1') - cst_config['reducao_cbs']
                cbs_valor = base_calculo * self.config_rti.cbs_aliquota * fator_reducao_cbs
                totais['CBS'] += cbs_valor
                totais['TOTAL'] += cbs_valor
            
            # Calcula IBS
            if cst_config['exige_trib'] and not cst_config['diferimento']:
                fator_reducao_ibs = Decimal('1') - cst_config['reducao_ibs']
                ibs_valor = base_calculo * self.config_rti.ibs_aliquota * fator_reducao_ibs
                totais['IBS'] += ibs_valor
                totais['TOTAL'] += ibs_valor
        
        return totais
    
    def calcular_detalhes_por_item(self, nota_fiscal: NotaFiscal) -> List[Dict[str, Any]]:
        """Calcula detalhamento por item da nota fiscal"""
        detalhes = []
        
        for item in nota_fiscal.itens:
            # Tributos atuais do item
            tributos_atuais = {
                'PIS': Decimal('0'),
                'COFINS': Decimal('0'),
                'IPI': Decimal('0'),
                'ICMS': Decimal('0')
            }
            
            for tributo in item.tributos:
                tipo = tributo.tipo.upper()
                if tipo in tributos_atuais:
                    tributos_atuais[tipo] = tributo.valor
            
            total_atual = sum(tributos_atuais.values())
            
            # Tributos RTI do item
            base_calculo = item.valor_total
            
            # Busca melhor configuração CST
            cst_configs = []
            csts_item = []
            for tributo in item.tributos:
                if tributo.cst:
                    config = self.get_cst_config(tributo.cst)
                    cst_configs.append(config)
                    csts_item.append(tributo.cst)
            
            if not cst_configs:
                cst_config = self.get_cst_config('')
                csts_item = ['N/A']
            else:
                cst_config = min(cst_configs, key=lambda x: (x['exige_trib'], -x['reducao_cbs'], -x['reducao_ibs']))
            
            # CBS
            cbs_valor = Decimal('0')
            if cst_config['exige_trib'] and not cst_config['monofasica']:
                fator_reducao_cbs = Decimal('1') - cst_config['reducao_cbs']
                cbs_valor = base_calculo * self.config_rti.cbs_aliquota * fator_reducao_cbs
            
            # IBS
            ibs_valor = Decimal('0')
            if cst_config['exige_trib'] and not cst_config['diferimento']:
                fator_reducao_ibs = Decimal('1') - cst_config['reducao_ibs']
                ibs_valor = base_calculo * self.config_rti.ibs_aliquota * fator_reducao_ibs
            
            total_rti = cbs_valor + ibs_valor
            diferenca = total_rti - total_atual
            
            detalhe = {
                'item': item.numero,
                'descricao': item.descricao[:50] + '...' if len(item.descricao) > 50 else item.descricao,
                'ncm': item.ncm,
                'valor_produto': float(item.valor_total),
                'csts': ', '.join(set(csts_item)),
                'pis_atual': float(tributos_atuais['PIS']),
                'cofins_atual': float(tributos_atuais['COFINS']),
                'ipi_atual': float(tributos_atuais['IPI']),
                'icms_atual': float(tributos_atuais['ICMS']),
                'total_atual': float(total_atual),
                'cbs_novo': float(cbs_valor),
                'ibs_novo': float(ibs_valor),
                'total_rti': float(total_rti),
                'diferenca': float(diferenca),
                'economia_percentual': float((diferenca / total_atual * 100) if total_atual > 0 else 0)
            }
            
            detalhes.append(detalhe)
        
        return detalhes
    
    def calcular_comparativo(self, nota_fiscal: NotaFiscal) -> CalculoComparativo:
        """Calcula comparativo completo entre tributação atual e RTI"""
        
        # Calcula tributos atuais
        tributos_atuais = self.calcular_tributos_atuais(nota_fiscal)
        
        # Calcula tributos RTI
        tributos_rti = self.calcular_tributos_rti(nota_fiscal)
        
        # Calcula economia
        total_atual = tributos_atuais['TOTAL']
        total_rti = tributos_rti['TOTAL']
        economia_total = total_rti - total_atual  # Negativo = economia, positivo = aumento
        economia_percentual = (economia_total / total_atual * 100) if total_atual > 0 else Decimal('0')
        
        # Detalhes por item
        detalhes = self.calcular_detalhes_por_item(nota_fiscal)
        
        return CalculoComparativo(
            nota_fiscal=nota_fiscal,
            tributacao_atual=tributos_atuais,
            tributacao_nova=tributos_rti,
            economia_total=economia_total,
            economia_percentual=economia_percentual,
            detalhes_por_item=detalhes
        )
