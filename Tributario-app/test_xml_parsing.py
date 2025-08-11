#!/usr/bin/env python3
"""
Teste rápido do parser de NF-e
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.parser.nf_parser import NFParser, NFParserError

def test_xml_parsing():
    """Testa o parsing do XML fornecido"""
    xml_file_path = "C:/Users/thiago.santos/Desktop/PESSOAL/26250607750628000153650120006461081027022603.xml"
    
    if not os.path.exists(xml_file_path):
        print(f"❌ Arquivo não encontrado: {xml_file_path}")
        return False
    
    try:
        # Lê o arquivo
        with open(xml_file_path, 'r', encoding='utf-8') as f:
            xml_content = f.read()
        
        # Cria o parser
        parser = NFParser()
        
        # Faz o parsing
        nota_fiscal = parser.parse_nota_fiscal(xml_content)
        
        # Exibe resultados
        print("✅ Parsing realizado com sucesso!")
        print(f"📄 Número da NF: {nota_fiscal.numero}")
        print(f"💰 Valor total: R$ {nota_fiscal.valor_total_produtos}")
        print(f"📦 Número de itens: {len(nota_fiscal.itens)}")
        print(f"📅 Data emissão: {nota_fiscal.data_emissao}")
        
        # Mostra alguns tributos
        print("\n📊 Tributos encontrados:")
        for item in nota_fiscal.itens[:3]:  # Mostra apenas os 3 primeiros
            print(f"  🔸 {item.descricao[:30]}...")
            for tributo in item.tributos:
                print(f"    - {tributo.tipo}: R$ {tributo.valor}")
        
        if len(nota_fiscal.itens) > 3:
            print(f"  ... e mais {len(nota_fiscal.itens) - 3} itens")
        
        return True
        
    except NFParserError as e:
        print(f"❌ Erro de parsing: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 Testando Parser de NF-e...")
    print("=" * 50)
    
    success = test_xml_parsing()
    
    print("=" * 50)
    if success:
        print("✅ Teste concluído com SUCESSO!")
        print("🚀 A aplicação deve funcionar corretamente agora.")
    else:
        print("❌ Teste FALHOU!")
        print("🔧 Verifique os erros acima.")
