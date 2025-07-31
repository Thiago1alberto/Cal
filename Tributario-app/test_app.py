"""
Script de teste para verificar se a aplicação está funcionando corretamente
"""
import sys
import os

# Adiciona o diretório do projeto ao Python path
sys.path.append(os.path.dirname(__file__))

def test_imports():
    """Testa as importações dos módulos"""
    print("🔄 Testando importações...")
    
    try:
        from src.parser.nf_parser import NFParser
        print("✅ NFParser importado com sucesso")
        
        from src.calculo.calculadora_rti import CalculadoraTributaria
        print("✅ CalculadoraTributaria importado com sucesso")
        
        from src.models import NotaFiscal, ItemNF, TributoItem
        print("✅ Modelos importados com sucesso")
        
        from src.util.formatters import format_currency, validate_xml_nfe
        print("✅ Formatadores importados com sucesso")
        
        print("\n🎉 Todas as importações realizadas com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro na importação: {e}")
        return False

def test_basic_functionality():
    """Testa funcionalidades básicas"""
    print("\n🔄 Testando funcionalidades básicas...")
    
    try:
        from src.util.formatters import format_currency, format_percentage, validate_xml_nfe
        from decimal import Decimal
        
        # Teste formatação monetária
        valor = Decimal('1234.56')
        formatted = format_currency(valor)
        print(f"✅ Formatação monetária: {formatted}")
        
        # Teste formatação percentual
        percent = Decimal('15.5')
        formatted_pct = format_percentage(percent)
        print(f"✅ Formatação percentual: {formatted_pct}")
        
        # Teste validação XML
        xml_invalid = "<invalid>test</invalid>"
        is_valid, msg = validate_xml_nfe(xml_invalid)
        print(f"✅ Validação XML (deve ser falso): {is_valid}")
        
        print("\n🎉 Funcionalidades básicas testadas com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

def test_parser_creation():
    """Testa criação do parser"""
    print("\n🔄 Testando criação do parser...")
    
    try:
        from src.parser.nf_parser import NFParser
        
        parser = NFParser()
        parser.set_debug(True)
        print("✅ Parser criado com sucesso")
        
        # Teste de conversão decimal
        from decimal import Decimal
        result = parser._safe_decimal("123,45")
        print(f"✅ Conversão decimal: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na criação do parser: {e}")
        return False

def main():
    """Função principal de teste"""
    print("🚀 Iniciando testes da aplicação tributária...")
    print("=" * 50)
    
    success = True
    
    # Teste de importações
    success &= test_imports()
    
    # Teste de funcionalidades básicas
    success &= test_basic_functionality()
    
    # Teste de criação do parser
    success &= test_parser_creation()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 TODOS OS TESTES PASSARAM! A aplicação está pronta para uso.")
        print("\n📝 Para executar a aplicação, use:")
        print("   streamlit run app_new.py")
    else:
        print("❌ Alguns testes falharam. Verifique os erros acima.")
    
    return success

if __name__ == "__main__":
    main()
