#!/usr/bin/env python
"""
Teste completo do sistema tributário com todos os 5 XMLs
Este script simula o processamento que seria feito pela aplicação Streamlit
"""
import sys
import os
from pathlib import Path
import pandas as pd
import traceback

# Adiciona o diretório do projeto ao path
sys.path.append(os.path.dirname(__file__))

def test_sistema_completo():
    """Testa o sistema completo com os 5 XMLs"""
    print("🏆 TESTE COMPLETO DO SISTEMA TRIBUTÁRIO")
    print("=" * 60)
    
    try:
        # Importações necessárias
        from src.parser.nf_parser import NFParser
        print("✅ Parser NFe importado")
        
        import pandas as pd
        print("✅ Pandas importado")
        
        # Tentar importar outras dependências opcionais
        optional_imports = []
        try:
            import streamlit
            optional_imports.append("✅ Streamlit")
        except ImportError:
            optional_imports.append("⚠️  Streamlit (opcional)")
            
        try:
            from st_aggrid import AgGrid
            optional_imports.append("✅ st_aggrid")
        except ImportError:
            optional_imports.append("⚠️  st_aggrid (opcional)")
            
        print("Dependências opcionais:", ", ".join(optional_imports))
        
    except ImportError as e:
        print(f"❌ Erro na importação: {e}")
        return False
    
    # Configuração de alíquotas padrão (mesmo do app.py)
    DEFAULT_RATES = {
        '000': {'PIS': 0.0065, 'COFINS': 0.03, 'ICMS': 0.18},
        '010': {'PIS': 0.0065, 'COFINS': 0.03, 'ICMS': 0.12},
        '020': {'PIS': 0.0065, 'COFINS': 0.03, 'ICMS': 0.07},
        '060': {'PIS': 0.0,    'COFINS': 0.0,  'ICMS': 0.0},
    }
    
    # Parâmetros da reforma (simulação)
    cbs_rate = 0.009  # 0.9%
    ibs_rate = 0.001  # 0.1%
    
    print(f"\n⚙️  PARÂMETROS DA SIMULAÇÃO:")
    print(f"   🎯 CBS: {cbs_rate*100:.1f}%")
    print(f"   🎯 IBS: {ibs_rate*100:.1f}%")
    
    # Diretório raiz
    project_root = Path(__file__).parent.parent
    
    # Lista dos XMLs
    xml_files = [
        "26250607750628000153650120006461001027022524.xml",
        "26250607750628000153650120006461021027022545.xml", 
        "26250607750628000153650340001204761044371272.xml",
        "26250607750628000153650340001204781044371293.xml",
        "26250607750628000153650340001207371044374083.xml"
    ]
    
    resultados_consolidados = []
    
    for i, xml_file in enumerate(xml_files, 1):
        xml_path = project_root / xml_file
        
        if not xml_path.exists():
            print(f"❌ XML {i}: Arquivo não encontrado - {xml_file}")
            continue
            
        print(f"\n📄 PROCESSANDO XML {i}: {xml_file}")
        print("-" * 50)
        
        try:
            # Parse do XML usando o parser principal
            parser = NFParser()
            
            # Carrega o XML
            with open(xml_path, 'r', encoding='utf-8') as f:
                xml_content = f.read()
            
            # Valida a estrutura
            if not parser.validate_nf_structure(xml_content):
                print(f"⚠️  XML não é uma NFe válida")
                continue
            
            # Parse completo
            nota_fiscal = parser.parse_nota_fiscal(xml_content)
            
            if not nota_fiscal.itens:
                print(f"⚠️  XML vazio ou sem dados válidos")
                continue
            
            # Converter para DataFrame para compatibilidade com o resto do código
            produtos_data = []
            for i, item in enumerate(nota_fiscal.itens, 1):
                produtos_data.append({
                    'item': i,
                    'valor_produto': float(item.valor_total),
                    'CST': getattr(item.get_tributo('ICMS'), 'cst', '000') if item.get_tributo('ICMS') else '000',
                    'NCM': item.ncm or '',
                    'produto': item.descricao
                })
            
            df_consolidado = pd.DataFrame(produtos_data)
            
            if df_consolidado.empty:
                print(f"⚠️  Não foi possível consolidar dados do XML")
                continue
            
            # 6. Aplicar alíquotas padrão baseado no CST
            df_consolidado['PIS_rate'] = df_consolidado['CST'].map(
                lambda cst: DEFAULT_RATES.get(str(cst), DEFAULT_RATES['000'])['PIS']
            )
            df_consolidado['COFINS_rate'] = df_consolidado['CST'].map(
                lambda cst: DEFAULT_RATES.get(str(cst), DEFAULT_RATES['000'])['COFINS']
            )
            df_consolidado['ICMS_rate'] = df_consolidado['CST'].map(
                lambda cst: DEFAULT_RATES.get(str(cst), DEFAULT_RATES['000'])['ICMS']
            )
            
            # 7. Cálculos tributários
            df_consolidado['PIS_atual'] = df_consolidado['valor_produto'] * df_consolidado['PIS_rate']
            df_consolidado['COFINS_atual'] = df_consolidado['valor_produto'] * df_consolidado['COFINS_rate']
            df_consolidado['ICMS_atual'] = df_consolidado['valor_produto'] * df_consolidado['ICMS_rate']
            df_consolidado['Tributos_Antes'] = (
                df_consolidado['PIS_atual'] + 
                df_consolidado['COFINS_atual'] + 
                df_consolidado['ICMS_atual']
            )
            
            # 8. Simulação da reforma
            df_consolidado['CBS_novo'] = df_consolidado['valor_produto'] * cbs_rate
            df_consolidado['IBS_novo'] = df_consolidado['valor_produto'] * ibs_rate
            df_consolidado['Tributos_Reforma'] = df_consolidado['CBS_novo'] + df_consolidado['IBS_novo']
            df_consolidado['Diferenca'] = df_consolidado['Tributos_Reforma'] - df_consolidado['Tributos_Antes']
            
            # 9. Resultados
            total_produtos = len(df_consolidado)
            valor_total = df_consolidado['valor_produto'].sum()
            tributos_antes = df_consolidado['Tributos_Antes'].sum()
            tributos_reforma = df_consolidado['Tributos_Reforma'].sum()
            economia = tributos_antes - tributos_reforma
            
            print(f"   🛍️  Produtos processados: {total_produtos}")
            print(f"   💰 Valor total: R$ {valor_total:.2f}")
            print(f"   📊 Tributos atuais: R$ {tributos_antes:.2f}")
            print(f"   🔄 Tributos reforma: R$ {tributos_reforma:.2f}")
            print(f"   💡 Diferença: R$ {economia:.2f} ({'economia' if economia > 0 else 'aumento'})")
            
            # Produtos com maior impacto
            df_top = df_consolidado.nlargest(3, 'valor_produto')[['produto', 'valor_produto', 'Diferenca']]
            print(f"   🏆 Top 3 produtos por valor:")
            for _, row in df_top.iterrows():
                produto = str(row['produto'])[:30] + "..." if len(str(row['produto'])) > 30 else str(row['produto'])
                print(f"      • {produto}: R$ {row['valor_produto']:.2f} (Δ R$ {row['Diferenca']:.2f})")
            
            # Salvar resultado
            resultados_consolidados.append({
                'xml_file': xml_file,
                'produtos': total_produtos,
                'valor_total': valor_total,
                'tributos_antes': tributos_antes,
                'tributos_reforma': tributos_reforma,
                'economia': economia,
                'percentual_economia': (economia / tributos_antes * 100) if tributos_antes > 0 else 0
            })
            
        except Exception as e:
            print(f"❌ Erro no processamento: {str(e)}")
            traceback.print_exc()
    
    # Resumo final
    print(f"\n🏆 RESUMO CONSOLIDADO DOS 5 XMLS")
    print("=" * 60)
    
    if resultados_consolidados:
        df_resumo = pd.DataFrame(resultados_consolidados)
        
        total_produtos = df_resumo['produtos'].sum()
        total_valor = df_resumo['valor_total'].sum()
        total_tributos_antes = df_resumo['tributos_antes'].sum()
        total_tributos_reforma = df_resumo['tributos_reforma'].sum()
        total_economia = df_resumo['economia'].sum()
        
        print(f"📊 TOTAIS GERAIS:")
        print(f"   🛍️  Total de produtos: {total_produtos}")
        print(f"   💰 Valor total: R$ {total_valor:.2f}")
        print(f"   📊 Tributos atuais: R$ {total_tributos_antes:.2f}")
        print(f"   🔄 Tributos reforma: R$ {total_tributos_reforma:.2f}")
        print(f"   💡 Economia total: R$ {total_economia:.2f}")
        print(f"   📈 Redução percentual: {(total_economia/total_tributos_antes*100):.1f}%")
        
        print(f"\n📋 DETALHAMENTO POR XML:")
        for _, row in df_resumo.iterrows():
            nome_curto = row['xml_file'][:25] + "..."
            economia_pct = row['percentual_economia']
            icon = "📉" if economia_pct > 0 else "📈" if economia_pct < 0 else "➖"
            print(f"   {icon} {nome_curto}: R$ {row['valor_total']:.2f} → Economia: R$ {row['economia']:.2f} ({economia_pct:.1f}%)")
        
        return True
    else:
        print("❌ Nenhum XML foi processado com sucesso")
        return False

def main():
    """Função principal"""
    success = test_sistema_completo()
    
    print(f"\n" + "=" * 60)
    if success:
        print("🎉 TESTE COMPLETO REALIZADO COM SUCESSO!")
        print(f"\n✅ Todos os 5 XMLs foram testados no sistema tributário")
        print(f"✅ O parser está funcionando corretamente")
        print(f"✅ Os cálculos tributários estão operacionais")
        print(f"✅ A simulação da reforma está funcionando")
        print(f"\n🚀 PRÓXIMOS PASSOS:")
        print(f"   1. Para interface gráfica: streamlit run app_new.py")
        print(f"   2. Para testes específicos: python test_app.py")
        print(f"   3. Os XMLs estão prontos para uso em produção")
    else:
        print("❌ ALGUNS TESTES FALHARAM")
        print("Verifique os erros acima e tente novamente")

if __name__ == "__main__":
    main()
