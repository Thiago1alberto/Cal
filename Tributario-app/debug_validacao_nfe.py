#!/usr/bin/env python3
"""
Teste de debug para verificar porque a validação NFe está falhando
"""

import xml.etree.ElementTree as ET
import sys
import os

def debug_validacao_nfe():
    """Debug da validação NFe"""
    
    # XML de teste
    xml_path = "../26250607750628000153650120006461001027022524.xml"
    
    if not os.path.exists(xml_path):
        print("❌ XML não encontrado!")
        return
    
    print("🔍 DEBUG DA VALIDAÇÃO NFE")
    print("=" * 50)
    
    try:
        # Carrega o XML
        with open(xml_path, 'r', encoding='utf-8') as f:
            xml_content = f.read()
        
        print(f"✅ XML carregado: {len(xml_content)} caracteres")
        
        # Parse do XML
        root = ET.fromstring(xml_content)
        print(f"✅ Parse XML OK: tag raiz = {root.tag}")
        
        # Elementos a verificar
        nfe_elements = [
            './/infNFe',
            './/NFe', 
            './/nfeProc'
        ]
        
        print(f"\n🔍 VERIFICANDO ELEMENTOS NFE:")
        for element_path in nfe_elements:
            element = root.find(element_path)
            if element is not None:
                print(f"   ✅ {element_path}: ENCONTRADO (tag: {element.tag})")
            else:
                print(f"   ❌ {element_path}: NÃO ENCONTRADO")
        
        # Verificar com namespaces
        ns = {'nfe': 'http://www.portalfiscal.inf.br/nfe'}
        print(f"\n🔍 VERIFICANDO COM NAMESPACES:")
        
        nfe_elements_ns = [
            './/nfe:infNFe',
            './/nfe:NFe',
            './/nfe:nfeProc'
        ]
        
        for element_path in nfe_elements_ns:
            try:
                element = root.find(element_path, ns)
                if element is not None:
                    print(f"   ✅ {element_path}: ENCONTRADO (tag: {element.tag})")
                else:
                    print(f"   ❌ {element_path}: NÃO ENCONTRADO")
            except Exception as e:
                print(f"   ❌ {element_path}: ERRO - {e}")
        
        # Verificar elementos sem namespace
        print(f"\n🔍 ELEMENTOS DIRETOS (SEM NAMESPACE):")
        direct_elements = [
            'infNFe',
            'NFe',
            'nfeProc'
        ]
        
        for element_name in direct_elements:
            elements = root.findall(f".//{element_name}")
            if elements:
                print(f"   ✅ {element_name}: {len(elements)} encontrado(s)")
                for elem in elements[:2]:  # Mostra até 2
                    print(f"      └─ {elem.tag}")
            else:
                print(f"   ❌ {element_name}: NÃO ENCONTRADO")
        
        # Lista todas as tags do XML (primeiros 20)
        print(f"\n📋 PRIMEIRAS 20 TAGS DO XML:")
        all_elements = list(root.iter())
        for i, elem in enumerate(all_elements[:20]):
            tag_clean = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
            print(f"   {i+1:2d}. {tag_clean} ({elem.tag})")
        
        if len(all_elements) > 20:
            print(f"   ... e mais {len(all_elements)-20} elementos")
        
        # Busca por qualquer elemento que contenha "nfe" ou "NFe"
        print(f"\n🔍 BUSCA POR TAGS CONTENDO 'nfe' OU 'NFe':")
        nfe_tags = []
        for elem in all_elements:
            tag_clean = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
            if 'nfe' in tag_clean.lower() or 'NFe' in tag_clean:
                nfe_tags.append(tag_clean)
        
        if nfe_tags:
            unique_tags = list(set(nfe_tags))
            for tag in unique_tags[:10]:  # Primeiras 10
                print(f"   ✅ {tag}")
        else:
            print(f"   ❌ Nenhuma tag NFe encontrada")
            
    except Exception as e:
        print(f"❌ ERRO: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_validacao_nfe()
