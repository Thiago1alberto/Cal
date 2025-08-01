#!/usr/bin/env python3
"""
Teste da validação NFe corrigida
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

def test_validacao_corrigida():
    """Testa a validação NFe corrigida"""
    
    try:
        from src.parser.nf_parser import NFParser
        
        parser = NFParser()
        
        # XML de teste
        xml_path = "../26250607750628000153650120006461001027022524.xml"
        
        if not os.path.exists(xml_path):
            print("❌ XML não encontrado!")
            return
        
        print("🔍 TESTE DA VALIDAÇÃO NFE CORRIGIDA")
        print("=" * 50)
        
        # Carrega o XML
        with open(xml_path, 'r', encoding='utf-8') as f:
            xml_content = f.read()
        
        print(f"✅ XML carregado: {len(xml_content)} caracteres")
        
        # Testa a validação
        try:
            is_valid = parser.validate_nf_structure(xml_content)
            if is_valid:
                print(f"✅ VALIDAÇÃO PASSOU! XML é uma NFe válida")
            else:
                print(f"❌ VALIDAÇÃO FALHOU! XML não é reconhecido como NFe")
        except Exception as e:
            print(f"❌ ERRO NA VALIDAÇÃO: {e}")
            return
        
        # Se passou na validação, tenta o parse completo
        if is_valid:
            print(f"\n🔍 TESTANDO PARSE COMPLETO...")
            try:
                nota_fiscal = parser.parse_nota_fiscal(xml_content)
                print(f"✅ PARSE COMPLETO OK!")
                print(f"   📄 Número: {nota_fiscal.numero}")
                print(f"   🏪 Emitente: {nota_fiscal.razao_social_emitente}")
                print(f"   📦 Produtos: {len(nota_fiscal.itens)}")
                print(f"   💰 Valor total: R$ {nota_fiscal.valor_total_produtos:.2f}")
            except Exception as e:
                print(f"❌ ERRO NO PARSE COMPLETO: {e}")
                import traceback
                traceback.print_exc()
        
    except ImportError as e:
        print(f"❌ ERRO DE IMPORTAÇÃO: {e}")
    except Exception as e:
        print(f"❌ ERRO GERAL: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_validacao_corrigida()
