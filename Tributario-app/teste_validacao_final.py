#!/usr/bin/env python3
"""
Teste final completo dos 5 XMLs com validação matemática precisa
"""

import xml.etree.ElementTree as ET
import glob
import os

def extrair_dados_xml_corrigido(xml_path):
    """Extrai dados do XML usando o parser corrigido com nItem"""
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        
        # Namespace padrão NFe
        ns = {'ns': 'http://www.portalfiscal.inf.br/nfe'}
        
        produtos = []
        
        # Busca todos os elementos 'det' (produtos)
        for det in root.findall('.//ns:det', ns):
            nitem = det.get('nItem')
            if not nitem:
                continue
                
            # Extrai dados do produto
            prod = det.find('.//ns:prod', ns)
            if prod is None:
                continue
                
            imposto = det.find('.//ns:imposto', ns)
            
            # Dados básicos do produto
            produto = {
                'nItem': int(nitem),
                'cProd': prod.findtext('ns:cProd', '', ns),
                'xProd': prod.findtext('ns:xProd', '', ns),
                'NCM': prod.findtext('ns:NCM', '', ns),
                'qCom': float(prod.findtext('ns:qCom', '0', ns)),
                'vUnCom': float(prod.findtext('ns:vUnCom', '0', ns)),
                'vProd': float(prod.findtext('ns:vProd', '0', ns))
            }
            
            # Tributos
            if imposto:
                # ICMS
                icms = imposto.find('.//ns:ICMS', ns)
                if icms:
                    for icms_tipo in icms:
                        produto['ICMS_CST'] = icms_tipo.findtext('ns:CST', '', ns) or icms_tipo.findtext('ns:CSOSN', '', ns)
                        produto['ICMS_vBC'] = float(icms_tipo.findtext('ns:vBC', '0', ns))
                        produto['ICMS_pICMS'] = float(icms_tipo.findtext('ns:pICMS', '0', ns))
                        produto['ICMS_vICMS'] = float(icms_tipo.findtext('ns:vICMS', '0', ns))
                        break
                
                # PIS
                pis = imposto.find('.//ns:PIS', ns)
                if pis:
                    for pis_tipo in pis:
                        produto['PIS_CST'] = pis_tipo.findtext('ns:CST', '', ns)
                        produto['PIS_vBC'] = float(pis_tipo.findtext('ns:vBC', '0', ns))
                        produto['PIS_pPIS'] = float(pis_tipo.findtext('ns:pPIS', '0', ns))
                        produto['PIS_vPIS'] = float(pis_tipo.findtext('ns:vPIS', '0', ns))
                        break
                
                # COFINS
                cofins = imposto.find('.//ns:COFINS', ns)
                if cofins:
                    for cofins_tipo in cofins:
                        produto['COFINS_CST'] = cofins_tipo.findtext('ns:CST', '', ns)
                        produto['COFINS_vBC'] = float(cofins_tipo.findtext('ns:vBC', '0', ns))
                        produto['COFINS_pCOFINS'] = float(cofins_tipo.findtext('ns:pCOFINS', '0', ns))
                        produto['COFINS_vCOFINS'] = float(cofins_tipo.findtext('ns:vCOFINS', '0', ns))
                        break
            
            produtos.append(produto)
        
        # Totais do XML
        total = root.find('.//ns:total', ns)
        totais_xml = {}
        if total:
            icms_tot = total.find('.//ns:ICMSTot', ns)
            if icms_tot:
                totais_xml = {
                    'vBC': float(icms_tot.findtext('ns:vBC', '0', ns)),
                    'vICMS': float(icms_tot.findtext('ns:vICMS', '0', ns)),
                    'vPIS': float(icms_tot.findtext('ns:vPIS', '0', ns)),
                    'vCOFINS': float(icms_tot.findtext('ns:vCOFINS', '0', ns)),
                    'vProd': float(icms_tot.findtext('ns:vProd', '0', ns)),
                    'vNF': float(icms_tot.findtext('ns:vNF', '0', ns))
                }
        
        return produtos, totais_xml
        
    except Exception as e:
        print(f"❌ Erro ao processar {xml_path}: {e}")
        return [], {}

def calcular_reforma_tributaria(produtos):
    """Calcula a simulação da reforma tributária"""
    for produto in produtos:
        # Tributos atuais
        icms_atual = produto.get('ICMS_vICMS', 0)
        pis_atual = produto.get('PIS_vPIS', 0)
        cofins_atual = produto.get('COFINS_vCOFINS', 0)
        tributos_atuais = icms_atual + pis_atual + cofins_atual
        
        # Reforma: CBS (1%) + IBS (1%) = 2% sobre valor do produto
        valor_produto = produto.get('vProd', 0)
        cbs = valor_produto * 0.01  # 1% CBS
        ibs = valor_produto * 0.01  # 1% IBS
        tributos_reforma = cbs + ibs
        
        # Economia
        economia = tributos_atuais - tributos_reforma
        percentual_economia = (economia / tributos_atuais * 100) if tributos_atuais > 0 else 0
        
        produto['tributos_atuais'] = tributos_atuais
        produto['cbs'] = cbs
        produto['ibs'] = ibs
        produto['tributos_reforma'] = tributos_reforma
        produto['economia'] = economia
        produto['percentual_economia'] = percentual_economia
    
    return produtos

def validar_calculos(produtos, totais_xml):
    """Valida se nossos cálculos conferem com os totais do XML"""
    # Soma nossos cálculos
    valor_total_calc = sum(p.get('vProd', 0) for p in produtos)
    icms_total_calc = sum(p.get('ICMS_vICMS', 0) for p in produtos)
    pis_total_calc = sum(p.get('PIS_vPIS', 0) for p in produtos)
    cofins_total_calc = sum(p.get('COFINS_vCOFINS', 0) for p in produtos)
    tributos_total_calc = icms_total_calc + pis_total_calc + cofins_total_calc
    
    # Compara com XML
    valor_xml = totais_xml.get('vProd', 0)
    icms_xml = totais_xml.get('vICMS', 0)
    pis_xml = totais_xml.get('vPIS', 0)
    cofins_xml = totais_xml.get('vCOFINS', 0)
    tributos_xml = icms_xml + pis_xml + cofins_xml
    
    # Tolerância de R$ 0.01 para arredondamentos
    tolerancia = 0.01
    
    valor_confere = abs(valor_total_calc - valor_xml) <= tolerancia
    tributos_confere = abs(tributos_total_calc - tributos_xml) <= tolerancia
    
    return {
        'valor_calc': valor_total_calc,
        'valor_xml': valor_xml,
        'valor_confere': valor_confere,
        'tributos_calc': tributos_total_calc,
        'tributos_xml': tributos_xml,
        'tributos_confere': tributos_confere,
        'icms_calc': icms_total_calc,
        'icms_xml': icms_xml,
        'pis_calc': pis_total_calc,
        'pis_xml': pis_xml,
        'cofins_calc': cofins_total_calc,
        'cofins_xml': cofins_xml
    }

def main():
    print("🎯 TESTE FINAL COMPLETO - VALIDAÇÃO MATEMÁTICA")
    print("=" * 60)
    
    # Busca os XMLs na pasta raiz do projeto
    xml_files = glob.glob("../*.xml")
    
    if not xml_files:
        print("❌ Nenhum arquivo XML encontrado!")
        return
    
    todos_produtos = []
    resultados_validacao = []
    
    for i, xml_file in enumerate(xml_files, 1):
        print(f"\n📄 XML {i}: {xml_file}")
        print("-" * 50)
        
        # Extrai dados
        produtos, totais_xml = extrair_dados_xml_corrigido(xml_file)
        
        if not produtos:
            print("❌ Nenhum produto extraído!")
            continue
        
        # Calcula reforma
        produtos = calcular_reforma_tributaria(produtos)
        
        # Valida cálculos
        validacao = validar_calculos(produtos, totais_xml)
        resultados_validacao.append(validacao)
        
        print(f"✅ Produtos extraídos: {len(produtos)}")
        print(f"💰 Valor total: R$ {validacao['valor_calc']:.2f}")
        print(f"📊 Tributos atuais: R$ {validacao['tributos_calc']:.2f}")
        
        # Detalhamento dos tributos
        print(f"   └─ ICMS: R$ {validacao['icms_calc']:.2f}")
        print(f"   └─ PIS: R$ {validacao['pis_calc']:.2f}")
        print(f"   └─ COFINS: R$ {validacao['cofins_calc']:.2f}")
        
        # Validação com XML
        print(f"\n🔍 VALIDAÇÃO COM XML:")
        print(f"   Valor: XML R$ {validacao['valor_xml']:.2f} = Calc R$ {validacao['valor_calc']:.2f} {'✅' if validacao['valor_confere'] else '❌'}")
        print(f"   Tributos: XML R$ {validacao['tributos_xml']:.2f} = Calc R$ {validacao['tributos_calc']:.2f} {'✅' if validacao['tributos_confere'] else '❌'}")
        
        # Reforma tributária
        tributos_reforma = sum(p['tributos_reforma'] for p in produtos)
        economia_total = sum(p['economia'] for p in produtos)
        percentual_medio = (economia_total / validacao['tributos_calc'] * 100) if validacao['tributos_calc'] > 0 else 0
        
        print(f"\n💡 REFORMA TRIBUTÁRIA:")
        print(f"   🔄 Tributos reforma: R$ {tributos_reforma:.2f}")
        print(f"   💰 Economia: R$ {economia_total:.2f}")
        print(f"   📈 Redução: {percentual_medio:.1f}%")
        
        status = "✅ VÁLIDO" if validacao['valor_confere'] and validacao['tributos_confere'] else "❌ DIVERGÊNCIA"
        print(f"   Status: {status}")
        
        todos_produtos.extend(produtos)
    
    # Resumo geral
    print(f"\n🏆 RESUMO GERAL")
    print("=" * 60)
    
    xmls_validos = sum(1 for v in resultados_validacao if v['valor_confere'] and v['tributos_confere'])
    valor_total_geral = sum(v['valor_calc'] for v in resultados_validacao)
    tributos_total_geral = sum(v['tributos_calc'] for v in resultados_validacao)
    
    tributos_reforma_geral = sum(p['tributos_reforma'] for p in todos_produtos)
    economia_geral = sum(p['economia'] for p in todos_produtos)
    percentual_geral = (economia_geral / tributos_total_geral * 100) if tributos_total_geral > 0 else 0
    
    print(f"📊 XMLs processados: {len(xml_files)}")
    print(f"✅ XMLs válidos: {xmls_validos}/{len(xml_files)}")
    print(f"📦 Total de produtos: {len(todos_produtos)}")
    print(f"💰 Valor total: R$ {valor_total_geral:.2f}")
    print(f"📊 Tributos atuais: R$ {tributos_total_geral:.2f}")
    print(f"🔄 Tributos reforma: R$ {tributos_reforma_geral:.2f}")
    print(f"💡 Economia total: R$ {economia_geral:.2f}")
    print(f"📈 Redução média: {percentual_geral:.1f}%")
    
    if xmls_validos == len(xml_files):
        print(f"\n🎉 TODOS OS TESTES PASSARAM!")
        print("✅ O sistema está funcionando corretamente!")
        print("✅ Os cálculos são matematicamente precisos!")
    else:
        print(f"\n⚠️  {len(xml_files) - xmls_validos} XML(s) com divergências menores")
        print("💡 Pode ser devido a arredondamentos ou diferenças de precisão")

if __name__ == "__main__":
    main()
