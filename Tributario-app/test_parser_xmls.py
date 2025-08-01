#!/usr/bin/env python
"""
Teste específico do parser XML do sistema tributário com os 5 arquivos XML
"""
import sys
import os
from pathlib import Path
import pandas as pd

# Adiciona o diretório do projeto ao path
sys.path.append(os.path.dirname(__file__))

def test_parser_with_xmls():
    """Testa o parser com os 5 arquivos XML"""
    print("🔧 TESTE DO PARSER XML COM OS 5 ARQUIVOS")
    print("=" * 50)
    
    try:
        from src.parser.xml_parser import ler_xml_universal
        print("✅ Parser importado com sucesso")
    except ImportError as e:
        print(f"❌ Erro ao importar parser: {e}")
        return False
    
    # Diretório raiz do projeto
    project_root = Path(__file__).parent.parent
    
    # Lista dos arquivos XML
    xml_files = [
        "26250607750628000153650120006461001027022524.xml",
        "26250607750628000153650120006461021027022545.xml", 
        "26250607750628000153650340001204761044371272.xml",
        "26250607750628000153650340001204781044371293.xml",
        "26250607750628000153650340001207371044374083.xml"
    ]
    
    results = []
    
    for i, xml_file in enumerate(xml_files, 1):
        xml_path = project_root / xml_file
        
        if not xml_path.exists():
            print(f"❌ XML {i}: {xml_file} - Arquivo não encontrado")
            continue
            
        print(f"\n🔄 XML {i}: {xml_file}")
        try:
            # Parse do XML
            df_result = ler_xml_universal(str(xml_path))
            
            if df_result is not None and not df_result.empty:
                print(f"✅ Parse realizado com sucesso")
                print(f"   📊 Registros extraídos: {len(df_result)}")
                print(f"   📋 Colunas: {list(df_result.columns)}")
                
                # Análise dos dados extraídos
                produtos = df_result[df_result['path'].str.endswith('/prod/xProd')]
                valores = df_result[df_result['path'].str.endswith('/prod/vProd')]
                ncms = df_result[df_result['path'].str.endswith('/prod/NCM')]
                csts = df_result[df_result['tag'] == 'CST']
                
                print(f"   🛍️  Produtos encontrados: {len(produtos)}")
                print(f"   💰 Valores encontrados: {len(valores)}")
                print(f"   🏷️  NCMs encontrados: {len(ncms)}")
                print(f"   📊 CSTs encontrados: {len(csts)}")
                
                # Exibir alguns produtos como exemplo
                if len(produtos) > 0:
                    print(f"   📝 Exemplos de produtos:")
                    for idx, produto in produtos.head(3).iterrows():
                        print(f"      - {produto['text']}")
                
                # Calcular valor total se possível
                if len(valores) > 0:
                    try:
                        valores_numericos = pd.to_numeric(valores['text'], errors='coerce')
                        valor_total = valores_numericos.sum()
                        print(f"   💵 Valor total aproximado: R$ {valor_total:.2f}")
                    except Exception:
                        print(f"   💵 Não foi possível calcular valor total")
                
                results.append({
                    'arquivo': xml_file,
                    'status': 'sucesso',
                    'registros': len(df_result),
                    'produtos': len(produtos),
                    'valores': len(valores),
                    'ncms': len(ncms),
                    'csts': len(csts)
                })
                
            else:
                print(f"⚠️  Parse retornou resultado vazio")
                results.append({
                    'arquivo': xml_file,
                    'status': 'vazio',
                    'registros': 0,
                    'produtos': 0,
                    'valores': 0,
                    'ncms': 0,
                    'csts': 0
                })
                
        except Exception as e:
            print(f"❌ Erro no parse: {str(e)}")
            results.append({
                'arquivo': xml_file,
                'status': 'erro',
                'erro': str(e),
                'registros': 0,
                'produtos': 0,
                'valores': 0,
                'ncms': 0,
                'csts': 0
            })
    
    # Resumo dos resultados
    print(f"\n📊 RESUMO DOS TESTES")
    print("=" * 50)
    
    df_results = pd.DataFrame(results)
    if not df_results.empty:
        sucessos = len(df_results[df_results['status'] == 'sucesso'])
        vazios = len(df_results[df_results['status'] == 'vazio'])
        erros = len(df_results[df_results['status'] == 'erro'])
        
        print(f"✅ Sucessos: {sucessos}/{len(xml_files)}")
        print(f"⚠️  Vazios: {vazios}/{len(xml_files)}")
        print(f"❌ Erros: {erros}/{len(xml_files)}")
        
        if sucessos > 0:
            total_produtos = df_results['produtos'].sum()
            total_registros = df_results['registros'].sum()
            print(f"\n📊 Total de registros extraídos: {total_registros}")
            print(f"🛍️  Total de produtos identificados: {total_produtos}")
            
            # Exibir tabela resumo
            print(f"\n📋 DETALHAMENTO POR ARQUIVO:")
            for _, row in df_results.iterrows():
                status_icon = "✅" if row['status'] == 'sucesso' else "❌" if row['status'] == 'erro' else "⚠️"
                print(f"{status_icon} {row['arquivo'][:30]}... | Produtos: {row['produtos']} | Registros: {row['registros']}")
    
    return len(results) > 0 and any(r['status'] == 'sucesso' for r in results)

def main():
    """Função principal"""
    success = test_parser_with_xmls()
    
    if success:
        print(f"\n🎉 TESTES CONCLUÍDOS COM SUCESSO!")
        print(f"📝 Os arquivos XML estão prontos para uso no sistema tributário.")
        print(f"\n🚀 Próximos passos:")
        print(f"   1. Instalar dependências completas: pip install -r requirements.txt")
        print(f"   2. Executar aplicação: streamlit run app_new.py")
        print(f"   3. Fazer upload dos XMLs na interface para análise completa")
    else:
        print(f"\n❌ Alguns problemas foram encontrados nos testes.")
        print(f"Verifique os erros acima e tente novamente.")

if __name__ == "__main__":
    main()
