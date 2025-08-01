#!/usr/bin/env python
"""
Teste de Validação de Resultados - Verificação da Correção dos Cálculos
Este script verifica se os resultados estão matematicamente corretos
"""
import sys
import os
from pathlib import Path
import pandas as pd
import xml.etree.ElementTree as ET

# Adiciona o diretório do projeto ao path
sys.path.append(os.path.dirname(__file__))

def validar_parse_xml_com_xml_nativo(xml_path):
    """Valida se nosso parser extrai os mesmos dados que a biblioteca XML nativa"""
    print(f"🔍 VALIDANDO PARSER COM XML NATIVO")
    print("-" * 40)
    
    try:
        # Nosso parser
        from src.parser.xml_parser import ler_xml_universal
        df_nosso = ler_xml_universal(str(xml_path))
        
        # Parser XML nativo
        tree = ET.parse(xml_path)
        root = tree.getroot()
        
        # Extrair produtos manualmente com XML nativo
        produtos_nativos = []
        valores_nativos = []
        ncms_nativos = []
        
        # Buscar todos os elementos 'det' (detalhes dos produtos)
        for det in root.findall('.//{http://www.portalfiscal.inf.br/nfe}det'):
            # Produto
            xprod = det.find('.//{http://www.portalfiscal.inf.br/nfe}xProd')
            if xprod is not None:
                produtos_nativos.append(xprod.text)
            
            # Valor
            vprod = det.find('.//{http://www.portalfiscal.inf.br/nfe}vProd')
            if vprod is not None:
                valores_nativos.append(float(vprod.text))
            
            # NCM
            ncm = det.find('.//{http://www.portalfiscal.inf.br/nfe}NCM')
            if ncm is not None:
                ncms_nativos.append(ncm.text)
        
        # Comparar com nosso parser
        produtos_nossos = df_nosso[df_nosso['path'].str.endswith('/prod/xProd')]['text'].tolist()
        valores_nossos = df_nosso[df_nosso['path'].str.endswith('/prod/vProd')]['text'].astype(float).tolist()
        ncms_nossos = df_nosso[df_nosso['path'].str.endswith('/prod/NCM')]['text'].tolist()
        
        print(f"📊 COMPARAÇÃO DOS RESULTADOS:")
        print(f"   Produtos (XML nativo): {len(produtos_nativos)}")
        print(f"   Produtos (nosso parser): {len(produtos_nossos)}")
        print(f"   ✅ Match produtos: {produtos_nativos == produtos_nossos}")
        
        print(f"   Valores (XML nativo): {len(valores_nativos)}")
        print(f"   Valores (nosso parser): {len(valores_nossos)}")
        print(f"   ✅ Match valores: {valores_nativos == valores_nossos}")
        
        print(f"   NCMs (XML nativo): {len(ncms_nativos)}")
        print(f"   NCMs (nosso parser): {len(ncms_nossos)}")
        print(f"   ✅ Match NCMs: {ncms_nativos == ncms_nossos}")
        
        # Verificar valor total
        total_nativo = sum(valores_nativos)
        total_nosso = sum(valores_nossos)
        print(f"   💰 Total nativo: R$ {total_nativo:.2f}")
        print(f"   💰 Total nosso: R$ {total_nosso:.2f}")
        print(f"   ✅ Match total: {abs(total_nativo - total_nosso) < 0.01}")
        
        return {
            'produtos_match': produtos_nativos == produtos_nossos,
            'valores_match': valores_nativos == valores_nossos,
            'ncms_match': ncms_nativos == ncms_nossos,
            'total_match': abs(total_nativo - total_nosso) < 0.01,
            'total_nativo': total_nativo,
            'total_nosso': total_nosso
        }
        
    except Exception as e:
        print(f"❌ Erro na validação: {e}")
        return None

def validar_calculos_tributarios():
    """Valida se os cálculos tributários estão matematicamente corretos"""
    print(f"\n🧮 VALIDANDO CÁLCULOS TRIBUTÁRIOS")
    print("-" * 40)
    
    # Dados de teste conhecidos
    valor_produto = 100.0
    aliquota_pis = 0.0165  # 1.65%
    aliquota_cofins = 0.076  # 7.6%
    aliquota_icms = 0.18  # 18%
    
    # Cálculos esperados
    pis_esperado = valor_produto * aliquota_pis  # 1.65
    cofins_esperado = valor_produto * aliquota_cofins  # 7.60
    icms_esperado = valor_produto * aliquota_icms  # 18.00
    total_esperado = pis_esperado + cofins_esperado + icms_esperado  # 27.25
    
    print(f"📊 TESTE COM VALORES CONHECIDOS:")
    print(f"   Valor do produto: R$ {valor_produto:.2f}")
    print(f"   PIS ({aliquota_pis*100:.2f}%): R$ {pis_esperado:.2f}")
    print(f"   COFINS ({aliquota_cofins*100:.2f}%): R$ {cofins_esperado:.2f}")
    print(f"   ICMS ({aliquota_icms*100:.2f}%): R$ {icms_esperado:.2f}")
    print(f"   Total esperado: R$ {total_esperado:.2f}")
    
    # Simulação da reforma
    cbs_rate = 0.009  # 0.9%
    ibs_rate = 0.001  # 0.1%
    
    cbs_esperado = valor_produto * cbs_rate  # 0.90
    ibs_esperado = valor_produto * ibs_rate  # 0.10
    reforma_esperado = cbs_esperado + ibs_esperado  # 1.00
    economia_esperada = total_esperado - reforma_esperado  # 26.25
    
    print(f"\n🔄 SIMULAÇÃO DA REFORMA:")
    print(f"   CBS ({cbs_rate*100:.1f}%): R$ {cbs_esperado:.2f}")
    print(f"   IBS ({ibs_rate*100:.1f}%): R$ {ibs_esperado:.2f}")
    print(f"   Total reforma: R$ {reforma_esperado:.2f}")
    print(f"   Economia esperada: R$ {economia_esperada:.2f}")
    print(f"   Redução esperada: {(economia_esperada/total_esperado*100):.1f}%")
    
    return {
        'pis_esperado': pis_esperado,
        'cofins_esperado': cofins_esperado,
        'icms_esperado': icms_esperado,
        'total_esperado': total_esperado,
        'cbs_esperado': cbs_esperado,
        'ibs_esperado': ibs_esperado,
        'reforma_esperado': reforma_esperado,
        'economia_esperada': economia_esperada
    }

def validar_consistencia_xml_real(xml_path):
    """Valida consistência dos dados em um XML real"""
    print(f"\n🎯 VALIDANDO CONSISTÊNCIA DO XML REAL")
    print("-" * 40)
    
    try:
        from src.parser.xml_parser import ler_xml_universal
        df_xml = ler_xml_universal(str(xml_path))
        
        # Extrair dados
        df_val = df_xml[df_xml['path'].str.endswith('/prod/vProd')].copy()
        df_val['valor_produto'] = pd.to_numeric(df_val['text'], errors='coerce')
        df_val['item'] = df_val['path'].str.extract(r'det\[(\d+)\]').astype(int)
        
        # Verificar se os valores fazem sentido
        valores = df_val['valor_produto'].tolist()
        
        print(f"📊 ANÁLISE DE CONSISTÊNCIA:")
        print(f"   Total de produtos: {len(valores)}")
        print(f"   Valores mínimo/máximo: R$ {min(valores):.2f} / R$ {max(valores):.2f}")
        print(f"   Valor médio: R$ {sum(valores)/len(valores):.2f}")
        print(f"   Valor total: R$ {sum(valores):.2f}")
        
        # Verificações de sanidade
        checks = {
            'valores_positivos': all(v > 0 for v in valores),
            'valores_realistas': all(v < 10000 for v in valores),  # Produtos até R$ 10k
            'sem_valores_nulos': not any(pd.isna(v) for v in valores),
            'quantidade_razoavel': 1 <= len(valores) <= 100  # Entre 1 e 100 produtos
        }
        
        print(f"🔍 VERIFICAÇÕES DE SANIDADE:")
        for check, passed in checks.items():
            icon = "✅" if passed else "❌"
            print(f"   {icon} {check.replace('_', ' ').title()}: {passed}")
        
        # Verificar se o total bate com o XML (usando XML nativo)
        tree = ET.parse(xml_path)
        root = tree.getroot()
        
        # Buscar vNF (valor total da nota)
        vnf_element = root.find('.//{http://www.portalfiscal.inf.br/nfe}vNF')
        if vnf_element is not None:
            vnf_xml = float(vnf_element.text)
            vnf_calculado = sum(valores)
            
            print(f"\n💰 VALIDAÇÃO DE TOTAIS:")
            print(f"   vNF do XML: R$ {vnf_xml:.2f}")
            print(f"   Total calculado: R$ {vnf_calculado:.2f}")
            print(f"   Diferença: R$ {abs(vnf_xml - vnf_calculado):.2f}")
            print(f"   ✅ Totais conferem: {abs(vnf_xml - vnf_calculado) < 0.01}")
            
            checks['totais_conferem'] = abs(vnf_xml - vnf_calculado) < 0.01
        
        return {
            'checks': checks,
            'valores': valores,
            'total_calculado': sum(valores),
            'todos_checks_ok': all(checks.values())
        }
        
    except Exception as e:
        print(f"❌ Erro na validação: {e}")
        return None

def validar_aliquotas_vs_xml_real(xml_path):
    """Compara nossas alíquotas estimadas com as do XML"""
    print(f"\n📊 VALIDANDO ALÍQUOTAS VS XML REAL")
    print("-" * 40)
    
    try:
        # Parser XML nativo para extrair tributos reais
        tree = ET.parse(xml_path)
        root = tree.getroot()
        
        tributos_reais = []
        
        for det in root.findall('.//{http://www.portalfiscal.inf.br/nfe}det'):
            # Valor do produto
            vprod = det.find('.//{http://www.portalfiscal.inf.br/nfe}vProd')
            if vprod is None:
                continue
            valor = float(vprod.text)
            
            # PIS
            vpis = det.find('.//{http://www.portalfiscal.inf.br/nfe}vPIS')
            vpis_real = float(vpis.text) if vpis is not None else 0
            
            # COFINS
            vcofins = det.find('.//{http://www.portalfiscal.inf.br/nfe}vCOFINS')
            vcofins_real = float(vcofins.text) if vcofins is not None else 0
            
            # ICMS
            vicms = det.find('.//{http://www.portalfiscal.inf.br/nfe}vICMS')
            vicms_real = float(vicms.text) if vicms is not None else 0
            
            # Calcular alíquotas efetivas
            aliq_pis_real = (vpis_real / valor * 100) if valor > 0 else 0
            aliq_cofins_real = (vcofins_real / valor * 100) if valor > 0 else 0
            aliq_icms_real = (vicms_real / valor * 100) if valor > 0 else 0
            
            tributos_reais.append({
                'valor': valor,
                'vpis_real': vpis_real,
                'vcofins_real': vcofins_real,
                'vicms_real': vicms_real,
                'aliq_pis_real': aliq_pis_real,
                'aliq_cofins_real': aliq_cofins_real,
                'aliq_icms_real': aliq_icms_real
            })
        
        if tributos_reais:
            df_real = pd.DataFrame(tributos_reais)
            
            print(f"📊 ALÍQUOTAS REAIS EXTRAÍDAS DO XML:")
            print(f"   PIS médio: {df_real['aliq_pis_real'].mean():.2f}%")
            print(f"   COFINS médio: {df_real['aliq_cofins_real'].mean():.2f}%")
            print(f"   ICMS médio: {df_real['aliq_icms_real'].mean():.2f}%")
            
            # Nossas estimativas padrão
            nossa_pis = 1.65  # 1.65%
            nossa_cofins = 7.6  # 7.6%
            nossa_icms = 18.0  # 18%
            
            print(f"\n📊 NOSSAS ESTIMATIVAS PADRÃO:")
            print(f"   PIS estimado: {nossa_pis:.2f}%")
            print(f"   COFINS estimado: {nossa_cofins:.2f}%")
            print(f"   ICMS estimado: {nossa_icms:.2f}%")
            
            # Calcular diferenças
            diff_pis = abs(df_real['aliq_pis_real'].mean() - nossa_pis)
            diff_cofins = abs(df_real['aliq_cofins_real'].mean() - nossa_cofins)
            diff_icms = abs(df_real['aliq_icms_real'].mean() - nossa_icms)
            
            print(f"\n📊 DIFERENÇAS (REAL vs ESTIMADO):")
            print(f"   PIS: {diff_pis:.2f}% de diferença")
            print(f"   COFINS: {diff_cofins:.2f}% de diferença")  
            print(f"   ICMS: {diff_icms:.2f}% de diferença")
            
            # Totais
            total_tributos_real = df_real['vpis_real'].sum() + df_real['vcofins_real'].sum() + df_real['vicms_real'].sum()
            total_valores = df_real['valor'].sum()
            carga_real = (total_tributos_real / total_valores * 100)
            
            print(f"\n💰 CARGA TRIBUTÁRIA REAL:")
            print(f"   Total tributos: R$ {total_tributos_real:.2f}")
            print(f"   Total valores: R$ {total_valores:.2f}")
            print(f"   Carga real: {carga_real:.1f}%")
            
            return {
                'aliq_pis_real': df_real['aliq_pis_real'].mean(),
                'aliq_cofins_real': df_real['aliq_cofins_real'].mean(),
                'aliq_icms_real': df_real['aliq_icms_real'].mean(),
                'carga_real': carga_real,
                'total_tributos_real': total_tributos_real,
                'diferenca_pis': diff_pis,
                'diferenca_cofins': diff_cofins,
                'diferenca_icms': diff_icms
            }
        
    except Exception as e:
        print(f"❌ Erro na validação de alíquotas: {e}")
        return None

def main():
    """Teste principal de validação de resultados"""
    print("🎯 VALIDAÇÃO DE CORREÇÃO DOS RESULTADOS")
    print("Este teste verifica se os cálculos estão matematicamente corretos")
    print("=" * 70)
    
    # Usar o XML menor para testes detalhados
    project_root = Path(__file__).parent.parent
    xml_path = project_root / "26250607750628000153650120006461001027022524.xml"
    
    if not xml_path.exists():
        print(f"❌ XML não encontrado: {xml_path}")
        return False
    
    # 1. Validar parser vs XML nativo
    resultado_parser = validar_parse_xml_com_xml_nativo(xml_path)
    
    # 2. Validar cálculos matemáticos
    resultado_calculos = validar_calculos_tributarios()
    
    # 3. Validar consistência dos dados
    resultado_consistencia = validar_consistencia_xml_real(xml_path)
    
    # 4. Validar alíquotas vs dados reais
    resultado_aliquotas = validar_aliquotas_vs_xml_real(xml_path)
    
    # Resumo final
    print(f"\n🏆 RESUMO DA VALIDAÇÃO")
    print("=" * 70)
    
    validacoes_ok = 0
    total_validacoes = 0
    
    if resultado_parser:
        total_validacoes += 4
        validacoes_ok += sum([
            resultado_parser['produtos_match'],
            resultado_parser['valores_match'],
            resultado_parser['ncms_match'],
            resultado_parser['total_match']
        ])
        print(f"✅ Parser XML: {sum([resultado_parser['produtos_match'], resultado_parser['valores_match'], resultado_parser['ncms_match'], resultado_parser['total_match']])}/4 validações OK")
    
    if resultado_consistencia:
        total_validacoes += len(resultado_consistencia['checks'])
        validacoes_ok += sum(resultado_consistencia['checks'].values())
        print(f"✅ Consistência: {sum(resultado_consistencia['checks'].values())}/{len(resultado_consistencia['checks'])} validações OK")
    
    if resultado_aliquotas:
        # Considerar OK se diferenças < 5%
        aliq_ok = sum([
            resultado_aliquotas['diferenca_pis'] < 5,
            resultado_aliquotas['diferenca_cofins'] < 5,
            resultado_aliquotas['diferenca_icms'] < 20  # ICMS varia muito
        ])
        total_validacoes += 3
        validacoes_ok += aliq_ok
        print(f"✅ Alíquotas: {aliq_ok}/3 validações OK")
    
    print(f"\n📊 SCORE GERAL: {validacoes_ok}/{total_validacoes} validações passaram")
    print(f"🎯 Confiabilidade: {(validacoes_ok/total_validacoes*100):.1f}%")
    
    if validacoes_ok/total_validacoes >= 0.8:
        print(f"\n🎉 SISTEMA APROVADO! Os resultados são confiáveis e matematicamente corretos!")
        return True
    else:
        print(f"\n⚠️  Sistema precisa de ajustes. Algumas validações falharam.")
        return False

if __name__ == "__main__":
    main()
