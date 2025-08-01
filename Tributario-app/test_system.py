#!/usr/bin/env python3
"""
Teste rápido do sistema Streamlit
"""

import streamlit as st
import sys
import os

# Adiciona o diretório do projeto ao path
sys.path.append(os.path.dirname(__file__))

def test_imports():
    """Testa se todas as importações estão funcionando"""
    try:
        st.write("🔍 **Testando Importações...**")
        
        # Parser
        from src.parser.nf_parser import NFParser
        st.write("✅ NFParser importado")
        
        # Calculadora
        from src.calculo.calculadora_rti import CalculadoraTributaria
        st.write("✅ CalculadoraTributaria importado")
        
        # Modelos
        from src.models import ConfigTributacao, NotaFiscal, CalculoComparativo
        st.write("✅ Modelos importados")
        
        # Formatters
        from src.util.formatters import validate_xml_nfe
        st.write("✅ Formatters importados")
        
        return True
        
    except Exception as e:
        st.error(f"❌ Erro na importação: {e}")
        return False

def test_xml_processing():
    """Testa o processamento de XML"""
    try:
        st.write("🔍 **Testando Processamento XML...**")
        
        # XML de teste (caminho relativo)
        xml_path = "../26250607750628000153650120006461001027022524.xml"
        
        if not os.path.exists(xml_path):
            st.warning("⚠️ XML de teste não encontrado")
            return False
        
        # Carrega XML
        with open(xml_path, 'r', encoding='utf-8') as f:
            xml_content = f.read()
        
        st.write(f"✅ XML carregado: {len(xml_content)} caracteres")
        
        # Valida XML
        from src.util.formatters import validate_xml_nfe
        is_valid, error_msg = validate_xml_nfe(xml_content)
        
        if is_valid:
            st.write("✅ Validação passou")
        else:
            st.error(f"❌ Validação falhou: {error_msg}")
            return False
        
        # Faz parse
        from src.parser.nf_parser import NFParser
        parser = NFParser()
        nota_fiscal = parser.parse_nota_fiscal(xml_content)
        
        st.write(f"✅ Parse concluído:")
        st.write(f"   - Número: {nota_fiscal.numero}")
        st.write(f"   - Emitente: {nota_fiscal.razao_social_emitente}")
        st.write(f"   - Itens: {len(nota_fiscal.itens)}")
        st.write(f"   - Valor: R$ {nota_fiscal.valor_total_produtos:.2f}")
        
        return True
        
    except Exception as e:
        st.error(f"❌ Erro no processamento: {e}")
        import traceback
        st.code(traceback.format_exc())
        return False

def main():
    st.title("🔧 Teste do Sistema Tributário")
    st.markdown("---")
    
    # Teste de importações
    st.header("1. Teste de Importações")
    if test_imports():
        st.success("✅ Todas as importações funcionando!")
    else:
        st.stop()
    
    st.markdown("---")
    
    # Teste de XML
    st.header("2. Teste de Processamento XML")
    if test_xml_processing():
        st.success("✅ Processamento XML funcionando!")
    else:
        st.warning("⚠️ Problema no processamento XML")
    
    st.markdown("---")
    st.success("🎉 **Sistema está funcionando!**")
    st.info("💡 Agora você pode usar o aplicativo principal: `streamlit run app_new.py`")

if __name__ == "__main__":
    main()
