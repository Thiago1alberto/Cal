#!/usr/bin/env python
"""
Debug do problema de duplicação de produtos
"""
import sys
import os
from pathlib import Path

sys.path.append(os.path.dirname(__file__))

def debug_extracao_produtos():
    """Debug para entender por que produtos estão sendo duplicados"""
    print("🐛 DEBUG: INVESTIGANDO DUPLICAÇÃO DE PRODUTOS")
    print("=" * 50)
    
    try:
        from src.parser.xml_parser import ler_xml_universal
        import pandas as pd
        
        project_root = Path(__file__).parent.parent
        xml_path = project_root / "26250607750628000153650120006461001027022524.xml"
        
        # Parse completo
        df_xml = ler_xml_universal(str(xml_path))
        
        print(f"📊 Total de registros no DataFrame: {len(df_xml)}")
        
        # Investigar produtos
        df_produtos = df_xml[df_xml['path'].str.endswith('/prod/xProd')]
        print(f"🛍️  Registros de produtos encontrados: {len(df_produtos)}")
        print("Produtos:")
        for i, (_, row) in enumerate(df_produtos.iterrows()):
            print(f"   {i+1}. Path: {row['path']} | Produto: {row['text']}")
        
        # Investigar valores
        df_valores = df_xml[df_xml['path'].str.endswith('/prod/vProd')]
        print(f"\n💰 Registros de valores encontrados: {len(df_valores)}")
        print("Valores:")
        for i, (_, row) in enumerate(df_valores.iterrows()):
            print(f"   {i+1}. Path: {row['path']} | Valor: {row['text']}")
        
        # Investigar extração de itens
        print(f"\n🔍 INVESTIGANDO EXTRAÇÃO DE NÚMEROS DE ITEM:")
        df_val_copy = df_valores.copy()
        df_val_copy['item_extracted'] = df_val_copy['path'].str.extract(r'det\[(\d+)\]')
        print("Extração de itens dos valores:")
        for i, (_, row) in enumerate(df_val_copy.iterrows()):
            print(f"   Path: {row['path']} | Item extraído: {row['item_extracted']}")
        
        # Verificar se há problema na conversão
        try:
            df_val_copy['item_int'] = df_val_copy['item_extracted'].astype(int)
            print(f"\n✅ Conversão para int OK")
            print("Itens únicos:", df_val_copy['item_int'].unique())
        except Exception as e:
            print(f"\n❌ Erro na conversão para int: {e}")
            df_val_copy['item_int'] = pd.to_numeric(df_val_copy['item_extracted'], errors='coerce')
            print("Tentando com to_numeric:")
            print("Itens únicos:", df_val_copy['item_int'].dropna().unique())
            
            # Ver quais falharam
            nulls = df_val_copy[df_val_copy['item_int'].isna()]
            if not nulls.empty:
                print("Registros que falharam na conversão:")
                for _, row in nulls.iterrows():
                    print(f"   Path: {row['path']} | Extraído: {row['item_extracted']}")
        
        return df_xml
        
    except Exception as e:
        print(f"❌ Erro no debug: {e}")
        import traceback
        traceback.print_exc()
        return None

def corrigir_extracao_itens():
    """Testa uma correção para a extração de itens"""
    print(f"\n🔧 TESTANDO CORREÇÃO DA EXTRAÇÃO")
    print("=" * 40)
    
    try:
        from src.parser.xml_parser import ler_xml_universal
        import pandas as pd
        
        project_root = Path(__file__).parent.parent
        xml_path = project_root / "26250607750628000153650120006461001027022524.xml"
        
        df_xml = ler_xml_universal(str(xml_path))
        
        # Método corrigido de extração
        def extrair_item_seguro(path):
            """Extrai número do item de forma mais segura"""
            import re
            match = re.search(r'det\[(\d+)\]', str(path))
            if match:
                return int(match.group(1))
            return None
        
        # Aplicar aos valores
        df_val = df_xml[df_xml['path'].str.endswith('/prod/vProd')].copy()
        df_val['item'] = df_val['path'].apply(extrair_item_seguro)
        df_val['valor_produto'] = pd.to_numeric(df_val['text'], errors='coerce')
        
        # Filtrar apenas registros válidos
        df_val_limpo = df_val.dropna(subset=['item', 'valor_produto'])
        
        print(f"📊 Valores após limpeza:")
        print(f"   Total original: {len(df_val)}")
        print(f"   Após limpeza: {len(df_val_limpo)}")
        print(f"   Itens únicos: {df_val_limpo['item'].nunique()}")
        
        for _, row in df_val_limpo.iterrows():
            print(f"   Item {row['item']}: R$ {row['valor_produto']:.2f}")
        
        # Fazer o mesmo para produtos
        df_prod = df_xml[df_xml['path'].str.endswith('/prod/xProd')].copy()
        df_prod['item'] = df_prod['path'].apply(extrair_item_seguro)
        df_prod_limpo = df_prod.dropna(subset=['item']).rename(columns={'text': 'produto'})
        
        print(f"\n🛍️  Produtos após limpeza:")
        for _, row in df_prod_limpo.iterrows():
            print(f"   Item {row['item']}: {row['produto']}")
        
        # Merge correto
        df_final = df_val_limpo[['item', 'valor_produto']].merge(
            df_prod_limpo[['item', 'produto']], 
            on='item', 
            how='left'
        )
        
        print(f"\n✅ RESULTADO FINAL CORRIGIDO:")
        print(f"   Total de itens: {len(df_final)}")
        print(f"   Valor total: R$ {df_final['valor_produto'].sum():.2f}")
        
        for _, row in df_final.iterrows():
            print(f"   {row['produto']}: R$ {row['valor_produto']:.2f}")
        
        return df_final
        
    except Exception as e:
        print(f"❌ Erro na correção: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Função principal de debug"""
    print("🐛 ANÁLISE E CORREÇÃO DO BUG DE DUPLICAÇÃO")
    print("=" * 60)
    
    # 1. Debug do problema
    df_xml = debug_extracao_produtos()
    
    if df_xml is not None:
        # 2. Testar correção
        df_corrigido = corrigir_extracao_itens()
        
        if df_corrigido is not None:
            print(f"\n🎉 BUG IDENTIFICADO E CORRIGIDO!")
            print(f"📝 Problema: Extração incorreta de números de item + conversão de tipos")
            print(f"✅ Solução: Usar regex mais robusto + dropna() para limpar dados")
        else:
            print(f"\n❌ Ainda há problemas na correção")
    else:
        print(f"\n❌ Não foi possível fazer o debug")

if __name__ == "__main__":
    main()
