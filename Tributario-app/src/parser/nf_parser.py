"""
Parser moderno e robusto para Notas Fiscais Eletrônicas (NF-e e NFC-e)
"""
import xml.etree.ElementTree as ET
import xmltodict
from decimal import Decimal, InvalidOperation
from typing import List, Dict, Optional, Any
import re
from datetime import datetime

from ..models import NotaFiscal, ItemNF, TributoItem


class NFParserError(Exception):
    """Exceção customizada para erros de parsing de NF"""
    pass


class NFParser:
    """Parser moderno para Notas Fiscais Eletrônicas"""
    
    # Namespaces comuns da NF-e
    NAMESPACES = {
        'nfe': 'http://www.portalfiscal.inf.br/nfe',
        'nfce': 'http://www.portalfiscal.inf.br/nfe'
    }
    
    def __init__(self):
        self.debug_mode = False
    
    def set_debug(self, debug: bool = True):
        """Ativa/desativa modo debug"""
        self.debug_mode = debug
    
    def _debug_print(self, message: str):
        """Print debug se modo debug ativo"""
        if self.debug_mode:
            print(f"[DEBUG] {message}")
    
    def _safe_decimal(self, value: Any, default: Decimal = Decimal('0')) -> Decimal:
        """Converte valor para Decimal de forma segura"""
        if value is None:
            return default
        
        try:
            if isinstance(value, str):
                # Remove caracteres não numéricos exceto ponto e vírgula
                cleaned = re.sub(r'[^\d.,\-]', '', value)
                # Substitui vírgula por ponto se necessário
                if ',' in cleaned and '.' not in cleaned:
                    cleaned = cleaned.replace(',', '.')
                elif ',' in cleaned and '.' in cleaned:
                    # Se tem ambos, vírgula é separador de milhares
                    cleaned = cleaned.replace(',', '')
                
                return Decimal(cleaned) if cleaned else default
            
            return Decimal(str(value))
        except (InvalidOperation, ValueError, TypeError):
            self._debug_print(f"Erro ao converter '{value}' para Decimal, usando {default}")
            return default
    
    def _extract_text(self, element: Optional[ET.Element], path: str) -> Optional[str]:
        """Extrai texto de um elemento XML pelo path"""
        if element is None:
            return None
        
        try:
            found = element.find(path, self.NAMESPACES)
            return found.text.strip() if found is not None and found.text else None
        except Exception as e:
            self._debug_print(f"Erro ao extrair texto do path '{path}': {e}")
            return None
    
    def _extract_decimal(self, element: Optional[ET.Element], path: str, default: Decimal = Decimal('0')) -> Decimal:
        """Extrai valor decimal de um elemento XML"""
        text = self._extract_text(element, path)
        return self._safe_decimal(text, default)
    
    def validate_nf_structure(self, xml_content: str) -> bool:
        """Valida se o XML é uma NF-e ou NFC-e válida"""
        try:
            root = ET.fromstring(xml_content)
            
            # Debug: imprime informações do XML
            self._debug_print(f"Root tag: {root.tag}")
            self._debug_print(f"Root attribs: {root.attrib}")
            
            # Lista de elementos que indicam uma NF-e válida
            nfe_elements = [
                './/infNFe',  # Sem namespace
                './/{http://www.portalfiscal.inf.br/nfe}infNFe',  # Com namespace completo
                './/NFe',  # Elemento NFe
                './/{http://www.portalfiscal.inf.br/nfe}NFe',  # NFe com namespace
                './/nfeProc',  # Processo da NF-e
                './/{http://www.portalfiscal.inf.br/nfe}nfeProc'  # nfeProc com namespace
            ]
            
            for element_path in nfe_elements:
                element = root.find(element_path)
                if element is not None:
                    self._debug_print(f"Elemento encontrado: {element_path} -> {element.tag}")
                    return True
            
            # Se não encontrou pelos métodos acima, tenta uma validação mais flexível
            # Procura por qualquer elemento que contenha 'infNFe' ou 'NFe'
            for elem in root.iter():
                if 'infNFe' in elem.tag or 'NFe' in elem.tag:
                    self._debug_print(f"Elemento flexível encontrado: {elem.tag}")
                    return True
            
            self._debug_print("Nenhum elemento de NF-e encontrado")
            return False
            
        except ET.ParseError as e:
            self._debug_print(f"Erro de parsing XML: {e}")
            raise NFParserError(f"XML inválido: {e}")
    
    def parse_xml_to_dict(self, xml_content: str) -> Dict[str, Any]:
        """Converte XML para dicionário usando xmltodict"""
        try:
            return xmltodict.parse(xml_content)
        except Exception as e:
            raise NFParserError(f"Erro ao converter XML para dicionário: {e}")
    
    def extract_basic_info(self, root: ET.Element) -> Dict[str, str]:
        """Extrai informações básicas da nota fiscal"""
        info = {}
        
        # Tenta diferentes estruturas de NF-e
        inf_nfe = (root.find('.//infNFe') or 
                  root.find('.//nfe:infNFe', self.NAMESPACES) or
                  root.find('.//{http://www.portalfiscal.inf.br/nfe}infNFe'))
        
        if inf_nfe is None:
            raise NFParserError("Estrutura infNFe não encontrada no XML")
        
        # Informações da nota
        ide = inf_nfe.find('.//ide') or inf_nfe.find('.//{http://www.portalfiscal.inf.br/nfe}ide')
        if ide is not None:
            info['numero'] = self._extract_text(ide, './/nNF') or self._extract_text(ide, './/{http://www.portalfiscal.inf.br/nfe}nNF') or ''
            info['serie'] = self._extract_text(ide, './/serie') or self._extract_text(ide, './/{http://www.portalfiscal.inf.br/nfe}serie') or ''
            
            # Data de emissão
            data_emissao = (self._extract_text(ide, './/dhEmi') or 
                          self._extract_text(ide, './/{http://www.portalfiscal.inf.br/nfe}dhEmi') or
                          self._extract_text(ide, './/dEmi') or
                          self._extract_text(ide, './/{http://www.portalfiscal.inf.br/nfe}dEmi'))
            
            info['data_emissao'] = data_emissao[:10] if data_emissao else ''
        
        # Chave de acesso
        info['chave_acesso'] = inf_nfe.get('Id', '').replace('NFe', '')
        
        # Emitente
        emit = inf_nfe.find('.//emit') or inf_nfe.find('.//{http://www.portalfiscal.inf.br/nfe}emit')
        if emit is not None:
            info['cnpj_emitente'] = self._extract_text(emit, './/CNPJ') or self._extract_text(emit, './/{http://www.portalfiscal.inf.br/nfe}CNPJ') or ''
            info['razao_social_emitente'] = self._extract_text(emit, './/xNome') or self._extract_text(emit, './/{http://www.portalfiscal.inf.br/nfe}xNome') or ''
        
        # Destinatário
        dest = inf_nfe.find('.//dest') or inf_nfe.find('.//{http://www.portalfiscal.inf.br/nfe}dest')
        if dest is not None:
            info['cnpj_destinatario'] = (self._extract_text(dest, './/CNPJ') or 
                                       self._extract_text(dest, './/{http://www.portalfiscal.inf.br/nfe}CNPJ') or
                                       self._extract_text(dest, './/CPF') or
                                       self._extract_text(dest, './/{http://www.portalfiscal.inf.br/nfe}CPF') or '')
            info['razao_social_destinatario'] = self._extract_text(dest, './/xNome') or self._extract_text(dest, './/{http://www.portalfiscal.inf.br/nfe}xNome') or ''
        
        return info
    
    def extract_tributos(self, det_element: ET.Element) -> List[TributoItem]:
        """Extrai tributos de um item da nota fiscal"""
        tributos = []
        
        # Busca elemento de impostos
        imposto = det_element.find('.//imposto') or det_element.find('.//{http://www.portalfiscal.inf.br/nfe}imposto')
        if imposto is None:
            return tributos
        
        # PIS
        pis_elements = imposto.findall('.//PIS') + imposto.findall('.//{http://www.portalfiscal.inf.br/nfe}PIS')
        for pis in pis_elements:
            cst = self._extract_text(pis, './/CST') or self._extract_text(pis, './/{http://www.portalfiscal.inf.br/nfe}CST') or ''
            
            # Tenta diferentes estruturas (PISAliq, PISQtde, PISNT, etc.)
            valor = (self._extract_decimal(pis, './/vPIS') or 
                    self._extract_decimal(pis, './/{http://www.portalfiscal.inf.br/nfe}vPIS'))
            
            base_calc = (self._extract_decimal(pis, './/vBC') or
                        self._extract_decimal(pis, './/{http://www.portalfiscal.inf.br/nfe}vBC'))
            
            aliquota = (self._extract_decimal(pis, './/pPIS') or
                       self._extract_decimal(pis, './/{http://www.portalfiscal.inf.br/nfe}pPIS'))
            
            if valor > 0 or cst:
                tributos.append(TributoItem(
                    tipo='PIS',
                    cst=cst,
                    base_calculo=base_calc,
                    aliquota=aliquota / 100 if aliquota > 0 else Decimal('0'),
                    valor=valor
                ))
        
        # COFINS
        cofins_elements = imposto.findall('.//COFINS') + imposto.findall('.//{http://www.portalfiscal.inf.br/nfe}COFINS')
        for cofins in cofins_elements:
            cst = self._extract_text(cofins, './/CST') or self._extract_text(cofins, './/{http://www.portalfiscal.inf.br/nfe}CST') or ''
            
            valor = (self._extract_decimal(cofins, './/vCOFINS') or
                    self._extract_decimal(cofins, './/{http://www.portalfiscal.inf.br/nfe}vCOFINS'))
            
            base_calc = (self._extract_decimal(cofins, './/vBC') or
                        self._extract_decimal(cofins, './/{http://www.portalfiscal.inf.br/nfe}vBC'))
            
            aliquota = (self._extract_decimal(cofins, './/pCOFINS') or
                       self._extract_decimal(cofins, './/{http://www.portalfiscal.inf.br/nfe}pCOFINS'))
            
            if valor > 0 or cst:
                tributos.append(TributoItem(
                    tipo='COFINS',
                    cst=cst,
                    base_calculo=base_calc,
                    aliquota=aliquota / 100 if aliquota > 0 else Decimal('0'),
                    valor=valor
                ))
        
        # IPI
        ipi_elements = imposto.findall('.//IPI') + imposto.findall('.//{http://www.portalfiscal.inf.br/nfe}IPI')
        for ipi in ipi_elements:
            cst = self._extract_text(ipi, './/CST') or self._extract_text(ipi, './/{http://www.portalfiscal.inf.br/nfe}CST') or ''
            
            valor = (self._extract_decimal(ipi, './/vIPI') or
                    self._extract_decimal(ipi, './/{http://www.portalfiscal.inf.br/nfe}vIPI'))
            
            base_calc = (self._extract_decimal(ipi, './/vBC') or
                        self._extract_decimal(ipi, './/{http://www.portalfiscal.inf.br/nfe}vBC'))
            
            aliquota = (self._extract_decimal(ipi, './/pIPI') or
                       self._extract_decimal(ipi, './/{http://www.portalfiscal.inf.br/nfe}pIPI'))
            
            if valor > 0 or cst:
                tributos.append(TributoItem(
                    tipo='IPI',
                    cst=cst,
                    base_calculo=base_calc,
                    aliquota=aliquota / 100 if aliquota > 0 else Decimal('0'),
                    valor=valor
                ))
        
        # ICMS
        icms_elements = imposto.findall('.//ICMS') + imposto.findall('.//{http://www.portalfiscal.inf.br/nfe}ICMS')
        for icms in icms_elements:
            # ICMS pode ter várias sub-estruturas (ICMS00, ICMS10, etc.)
            for child in icms:
                if child.tag.startswith('ICMS') or child.tag.endswith('}ICMS'):
                    cst = (self._extract_text(child, './/CST') or 
                          self._extract_text(child, './/{http://www.portalfiscal.inf.br/nfe}CST') or
                          self._extract_text(child, './/CSOSN') or
                          self._extract_text(child, './/{http://www.portalfiscal.inf.br/nfe}CSOSN') or '')
                    
                    valor = (self._extract_decimal(child, './/vICMS') or
                            self._extract_decimal(child, './/{http://www.portalfiscal.inf.br/nfe}vICMS'))
                    
                    base_calc = (self._extract_decimal(child, './/vBC') or
                                self._extract_decimal(child, './/{http://www.portalfiscal.inf.br/nfe}vBC'))
                    
                    aliquota = (self._extract_decimal(child, './/pICMS') or
                               self._extract_decimal(child, './/{http://www.portalfiscal.inf.br/nfe}pICMS'))
                    
                    if valor > 0 or cst:
                        tributos.append(TributoItem(
                            tipo='ICMS',
                            cst=cst,
                            base_calculo=base_calc,
                            aliquota=aliquota / 100 if aliquota > 0 else Decimal('0'),
                            valor=valor
                        ))
                    break
        
        return tributos
    
    def parse_nota_fiscal(self, xml_content: str) -> NotaFiscal:
        """Faz o parse completo da nota fiscal"""
        
        # Valida estrutura
        if not self.validate_nf_structure(xml_content):
            raise NFParserError("Arquivo não é uma NF-e ou NFC-e válida")
        
        try:
            root = ET.fromstring(xml_content)
        except ET.ParseError as e:
            raise NFParserError(f"Erro ao fazer parse do XML: {e}")
        
        # Extrai informações básicas
        basic_info = self.extract_basic_info(root)
        
        # Busca infNFe
        inf_nfe = (root.find('.//infNFe') or 
                  root.find('.//nfe:infNFe', self.NAMESPACES) or
                  root.find('.//{http://www.portalfiscal.inf.br/nfe}infNFe'))
        
        # Extrai totais
        total = inf_nfe.find('.//total') or inf_nfe.find('.//{http://www.portalfiscal.inf.br/nfe}total')
        icms_tot = None
        if total is not None:
            icms_tot = total.find('.//ICMSTot') or total.find('.//{http://www.portalfiscal.inf.br/nfe}ICMSTot')
        
        valor_total_produtos = Decimal('0')
        valor_total_nota = Decimal('0')
        
        if icms_tot is not None:
            valor_total_produtos = (self._extract_decimal(icms_tot, './/vProd') or
                                   self._extract_decimal(icms_tot, './/{http://www.portalfiscal.inf.br/nfe}vProd'))
            valor_total_nota = (self._extract_decimal(icms_tot, './/vNF') or
                               self._extract_decimal(icms_tot, './/{http://www.portalfiscal.inf.br/nfe}vNF'))
        
        # Extrai itens
        itens = []
        det_elements = inf_nfe.findall('.//det') + inf_nfe.findall('.//{http://www.portalfiscal.inf.br/nfe}det')
        
        for i, det in enumerate(det_elements, 1):
            # Produto
            prod = det.find('.//prod') or det.find('.//{http://www.portalfiscal.inf.br/nfe}prod')
            if prod is None:
                continue
            
            # Extrai dados do produto
            descricao = self._extract_text(prod, './/xProd') or self._extract_text(prod, './/{http://www.portalfiscal.inf.br/nfe}xProd') or ''
            ncm = self._extract_text(prod, './/NCM') or self._extract_text(prod, './/{http://www.portalfiscal.inf.br/nfe}NCM') or ''
            cfop = self._extract_text(prod, './/CFOP') or self._extract_text(prod, './/{http://www.portalfiscal.inf.br/nfe}CFOP') or ''
            unidade = self._extract_text(prod, './/uCom') or self._extract_text(prod, './/{http://www.portalfiscal.inf.br/nfe}uCom') or ''
            
            quantidade = (self._extract_decimal(prod, './/qCom') or
                         self._extract_decimal(prod, './/{http://www.portalfiscal.inf.br/nfe}qCom', Decimal('1')))
            
            valor_unitario = (self._extract_decimal(prod, './/vUnCom') or
                             self._extract_decimal(prod, './/{http://www.portalfiscal.inf.br/nfe}vUnCom'))
            
            valor_total = (self._extract_decimal(prod, './/vProd') or
                          self._extract_decimal(prod, './/{http://www.portalfiscal.inf.br/nfe}vProd'))
            
            # Extrai tributos
            tributos = self.extract_tributos(det)
            
            item = ItemNF(
                numero=i,
                descricao=descricao,
                ncm=ncm,
                cfop=cfop,
                unidade=unidade,
                quantidade=quantidade,
                valor_unitario=valor_unitario,
                valor_total=valor_total,
                tributos=tributos
            )
            
            itens.append(item)
        
        return NotaFiscal(
            numero=basic_info.get('numero', ''),
            serie=basic_info.get('serie', ''),
            data_emissao=basic_info.get('data_emissao', ''),
            chave_acesso=basic_info.get('chave_acesso', ''),
            cnpj_emitente=basic_info.get('cnpj_emitente', ''),
            razao_social_emitente=basic_info.get('razao_social_emitente', ''),
            cnpj_destinatario=basic_info.get('cnpj_destinatario', ''),
            razao_social_destinatario=basic_info.get('razao_social_destinatario', ''),
            valor_total_produtos=valor_total_produtos,
            valor_total_nota=valor_total_nota,
            itens=itens
        )
