#!/usr/bin/env python
"""
Script para testar os 5 arquivos XML do sistema tributário
"""
import os
import sys
import traceback
from pathlib import Path

def test_xml_files():
    """Testa os 5 arquivos XML disponíveis"""
    print("🔬 Iniciando testes dos arquivos XML...")
    print("=" * 60)
    
    # Diretório raiz do projeto (um nível acima do Tributario-app)
    project_root = Path(__file__).parent.parent
    print(f"📁 Diretório do projeto: {project_root}")
    
    # Lista dos arquivos XML
    xml_files = [
        "26250607750628000153650120006461001027022524.xml",
        "26250607750628000153650120006461021027022545.xml", 
        "26250607750628000153650340001204761044371272.xml",
        "26250607750628000153650340001204781044371293.xml",
        "26250607750628000153650340001207371044374083.xml"
    ]
    
    # Verificar se os arquivos existem
    existing_files = []
    for xml_file in xml_files:
        xml_path = project_root / xml_file
        if xml_path.exists():
            existing_files.append(xml_path)
            print(f"✅ Encontrado: {xml_file}")
        else:
            print(f"❌ Não encontrado: {xml_file}")
    
    print(f"\n📊 Total de arquivos encontrados: {len(existing_files)}/5")
    
    if not existing_files:
        print("⚠️  Nenhum arquivo XML encontrado para teste!")
        return False
    
    # Teste básico: verificar se os arquivos são XMLs válidos
    print("\n🔍 Testando estrutura básica dos XMLs...")
    valid_xmls = []
    
    for xml_path in existing_files:
        try:
            # Teste básico de leitura
            with open(xml_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Verificar se é XML válido básico (NFe pode não ter declaração <?xml)
            if ('<nfeProc' in content or '<?xml' in content) and '<' in content and '>' in content:
                valid_xmls.append(xml_path)
                size_kb = xml_path.stat().st_size / 1024
                print(f"✅ {xml_path.name} - Tamanho: {size_kb:.1f} KB")
                
                # Detectar tipo de documento
                if '<nfeProc' in content:
                    print(f"   📄 Tipo: Nota Fiscal Eletrônica (NFe)")
                elif '<nfceProc' in content:
                    print(f"   📄 Tipo: Nota Fiscal de Consumidor Eletrônica (NFCe)")
                else:
                    print(f"   📄 Tipo: XML genérico")
            else:
                print(f"❌ {xml_path.name} - Não parece ser um XML válido")
                
        except Exception as e:
            print(f"❌ {xml_path.name} - Erro na leitura: {e}")
    
    print(f"\n📊 XMLs válidos: {len(valid_xmls)}/{len(existing_files)}")
    
    # Teste do parser se disponível
    print("\n🔧 Testando parser do sistema...")
    try:
        sys.path.append(str(Path(__file__).parent))
        from src.parser.xml_parser import ler_xml_universal
        
        print("✅ Parser importado com sucesso")
        
        # Testar cada XML válido
        parsed_successfully = 0
        for xml_path in valid_xmls:
            try:
                print(f"\n🔄 Processando: {xml_path.name}")
                df_result = ler_xml_universal(str(xml_path))
                
                if df_result is not None and not df_result.empty:
                    print(f"✅ Parse realizado com sucesso - {len(df_result)} registros extraídos")
                    print(f"   Colunas: {list(df_result.columns)}")
                    parsed_successfully += 1
                else:
                    print(f"⚠️  Parse retornou resultado vazio")
                    
            except Exception as e:
                print(f"❌ Erro no parse: {str(e)}")
                traceback.print_exc()
        
        print(f"\n📊 XMLs processados com sucesso: {parsed_successfully}/{len(valid_xmls)}")
        
    except ImportError as e:
        print(f"⚠️  Não foi possível importar o parser: {e}")
        print("   Teste limitado à validação básica de estrutura")
    
    return len(valid_xmls) > 0

def main():
    """Função principal"""
    print("🧪 TESTE DOS ARQUIVOS XML DO SISTEMA TRIBUTÁRIO")
    print("=" * 60)
    
    success = test_xml_files()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 Testes concluídos! Pelo menos alguns XMLs foram validados.")
        print("\n📝 Próximos passos:")
        print("   1. Instalar dependências: pip install -r requirements.txt")
        print("   2. Executar aplicação: streamlit run app_new.py")
        print("   3. Fazer upload dos XMLs na interface")
    else:
        print("❌ Testes falharam. Verifique se os arquivos XML estão no local correto.")
    
    return success

if __name__ == "__main__":
    main()
