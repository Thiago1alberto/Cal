import os
import re
import json
import streamlit as st
import pandas as pd
from src.parser.xml_parser import ler_xml_universal
from st_aggrid import AgGrid, GridOptionsBuilder

# Default de alíquotas se não houver arquivo JSON
DEFAULT_RATES = {
    '000': {'PIS': 0.0065, 'COFINS': 0.03, 'ICMS': 0.18},
    '010': {'PIS': 0.0065, 'COFINS': 0.03, 'ICMS': 0.12},
    '020': {'PIS': 0.0065, 'COFINS': 0.03, 'ICMS': 0.07},
    '060': {'PIS': 0.0,    'COFINS': 0.0,  'ICMS': 0.0},
}
BOOL_MAP = {'SIM': True, 'NÃO': False, 'NAO': False}

def extrai_item(path: str) -> int:
    """Extrai índice do item do XML a partir do path 'det[i]'."""
    m = re.search(r"det\[(\d+)\]", path)
    return int(m.group(1)) if m else -1


def fmt(valor: float) -> str:
    """Formata número como moeda brasileira: R$ 1.234,56"""
    s = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {s}"


def main():
    st.set_page_config(page_title="Relatório Tributário", layout="wide")
    st.title('🌟 Relatório Executivo & Simulação (CBS+IBS)')

    # Diagnóstico da PLP
    st.header('🔎 Diagnóstico da PLP 39/2015')
    st.markdown(
        """
        A Reforma Tributária (PLP 39/2015) propõe:
        - Substituir PIS/COFINS por **CBS** de alíquota única.
        - Implantar **IBS** sobre consumo interno.
        - Unificar e simplificar a tributação de comércio, indústria e serviços.
        """
    )
    st.markdown('---')

    # Upload dos arquivos
    xml_upl = st.file_uploader('📄 XML de NF‑e', type='xml')
    cst_upl = st.file_uploader('📊 Planilha de CST e Classificações', type=['xls','xlsx'])
    if not xml_upl or not cst_upl:
        st.info('Carregue o XML e a planilha CST para prosseguir.')
        return

        # Processamento da planilha CST
    raw = pd.read_excel(cst_upl, header=None, dtype=str)
    header_row = raw.apply(lambda r: r.astype(str).str.contains('CST', na=False).any(), axis=1).idxmax()
    cst_df = pd.read_excel(cst_upl, header=header_row)
    cst_df = cst_df.loc[:, ~cst_df.columns.str.contains('^Unnamed')]
    # Remove espaços em branco de colunas
    cst_df.columns = cst_df.columns.str.strip()
    # Debug colunas CST
    st.write('▶ CST columns:', list(cst_df.columns))
    if 'CST' not in cst_df.columns and 'Código' in cst_df.columns:
        cst_df.rename(columns={'Código':'CST'}, inplace=True)
    cst_df['CST'] = cst_df['CST'].astype(str).str.strip()
    # Flags booleans
    for flag in ['Exige Trib','Monofásica','Red. Alíq','Diferimento']:
        cst_df[flag] = cst_df.get(flag,'NÃO').map(lambda v: BOOL_MAP.get(str(v).upper(), False))
    # Percentuais de redução
    for pct in ['% Red. IBS','% Red. CBS']:
        if pct in cst_df.columns:
            col = cst_df[pct].astype(str).str.rstrip('%')
            cst_df[pct] = pd.to_numeric(col, errors='coerce').fillna(0) / 100
        else:
            cst_df[pct] = 0.0
    # Alíquotas do CST
    rates_dict = DEFAULT_RATES
    if os.path.exists('aliquotas.json'):
        rates_dict = json.load(open('aliquotas.json', encoding='utf-8'))
    rates_df = pd.DataFrame.from_dict(rates_dict, orient='index').reset_index().rename(columns={'index':'CST'})
    rates_df['CST'] = rates_df['CST'].astype(str).str.strip()
    rates_df['PIS'] = pd.to_numeric(rates_df.get('PIS',0),errors='coerce').fillna(0)
    rates_df['COFINS'] = pd.to_numeric(rates_df.get('COFINS',0),errors='coerce').fillna(0)
    rates_df['ICMS'] = rates_df.get('ICMS',0).apply(lambda v: float(v) if str(v).replace('.','',1).isdigit() else v)
    fb = DEFAULT_RATES['000']
    for col in ['PIS','COFINS','ICMS']:
        rates_df[col] = rates_df[col].where(rates_df[col].notna(), fb[col])
    cst_df = cst_df.merge(rates_df, on='CST', how='left')

    # Parâmetros da Reforma
    st.sidebar.header('⚙️ Simulação Reforma')
    cbs_rate = st.sidebar.number_input('CBS (%)', 0.0, 100.0, 0.9) / 100
    ibs_rate = st.sidebar.number_input('IBS (%)', 0.0, 100.0, 0.1) / 100
    st.markdown('---')

    # Parse do XML e extração de dados
    tmp = 'temp_nf.xml'
    open(tmp, 'wb').write(xml_upl.read())
    df_xml = ler_xml_universal(tmp)
    os.remove(tmp)

    # Valores do XML
    df_val = df_xml[df_xml['path'].str.endswith('/prod/vProd')].assign(valor_produto=lambda d: d['text'].astype(float))[['path','valor_produto']]
    df_val['item'] = df_val['path'].apply(extrai_item)
    # CST do XML
    df_cstxml = df_xml[df_xml['tag']=='CST'].rename(columns={'text':'CST'})[['path','CST']]
    df_cstxml['item'] = df_cstxml['path'].apply(extrai_item)
    # Merge CST + valores
    df_itens = df_val.merge(df_cstxml[['item','CST']], on='item', how='left').merge(cst_df, on='CST', how='left')

    # Integração NCM + tributos JSON
    try:
        ncm_dict = json.load(open('ncm_rates.json', encoding='utf-8'))
    except FileNotFoundError:
        st.error('ncm_rates.json não encontrado.'); return
    rates_ncm = pd.DataFrame.from_dict(ncm_dict, orient='index').reset_index().rename(columns={'index':'ncm'})
    rates_ncm.rename(columns={'PIS':'PIS_json','COFINS':'COFINS_json','IPI':'IPI_json'}, inplace=True)
    rates_ncm['ncm'] = rates_ncm['ncm'].astype(str).str.zfill(8)
    for col in ['PIS_json','COFINS_json','IPI_json']:
        rates_ncm[col] = pd.to_numeric(rates_ncm.get(col,0), errors='coerce').fillna(0)
    df_ncm = df_xml[df_xml['path'].str.endswith('/prod/NCM')].assign(ncm=lambda d: d['text'])[['path','ncm']]
    df_ncm['item'] = df_ncm['path'].apply(extrai_item)
    df_all = df_itens.merge(df_ncm[['item','ncm']], on='item', how='left').merge(rates_ncm, on='ncm', how='left')
    # Nome do produto
    df_prod = df_xml[df_xml['path'].str.endswith('/prod/xProd')].assign(produto=lambda d: d['text'])[['path','produto']]
    df_prod['item'] = df_prod['path'].apply(extrai_item)
    df_all = df_all.merge(df_prod[['item','produto']], on='item', how='left')

    # Cálculos Antes da Reforma
    # Preparação de dados numéricos
    # Coerce valor_produto para float e preencher nulos
    df_all['valor_produto'] = pd.to_numeric(df_all['valor_produto'], errors='coerce').fillna(0)
    # Garantir colunas de redução existam e preencham nulos
    for pct_col in ['% Red. CBS','% Red. IBS']:
        if pct_col in df_all.columns:
            df_all[pct_col] = pd.to_numeric(df_all[pct_col], errors='coerce').fillna(0)
        else:
            df_all[pct_col] = 0.0
    # Cálculos Antes da Reforma
    df_all[['PIS_json','COFINS_json','IPI_json']] = df_all[['PIS_json','COFINS_json','IPI_json']].fillna(0)
    df_all['valor_pis']    = df_all['valor_produto'] * df_all['PIS_json']
    df_all['valor_cofins'] = df_all['valor_produto'] * df_all['COFINS_json']
    df_all['valor_ipi']    = df_all['valor_produto'] * df_all['IPI_json']
    df_all['valor_icms']   = df_all.apply(lambda r: r['valor_produto'] * r['ICMS'] if isinstance(r['ICMS'], (int,float)) else 0, axis=1)
    df_all['Despesa Antes Reforma'] = df_all[['valor_pis','valor_cofins','valor_icms','valor_ipi']].sum(axis=1)

    # Cálculos Pós da Reforma
    df_all['CBS (%)']             = df_all['valor_produto'] * cbs_rate * (1 - df_all['% Red. CBS'])
    df_all['IBS (%)']             = df_all['valor_produto'] * ibs_rate * (1 - df_all['% Red. IBS'])
    df_all['Despesa Pós Reforma'] = df_all['CBS (%)'] + df_all['IBS (%)']
    df_all['Diferença Tributária'] = df_all['Despesa Pós Reforma'] - df_all['Despesa Antes Reforma']

    # Debug de tipos e valores
    st.write("▶ Debug de Tipos e Valores:")
    debug_cols = ['valor_produto','% Red. CBS','CBS (%)','% Red. IBS','IBS (%)']
    st.write(df_all[debug_cols].dtypes)
    st.write(df_all[debug_cols].head(5))
    st.write(f"cbs_rate = {cbs_rate}, ibs_rate = {ibs_rate}")

    # Resumo Consolidado
    total_produto = df_all['valor_produto'].sum()
    total_ipi     = df_all['valor_ipi'].sum()
    desp_atual    = df_all['Despesa Antes Reforma'].sum()
    cbs_val       = df_all['CBS (%)'].sum()
    ibs_val       = df_all['IBS (%)'].sum()
    cbs_ibs       = df_all['Despesa Pós Reforma'].sum()
    diff_val      = df_all['Diferença Tributária'].sum()

    st.header('📊 Resumo Consolidado dos Tributos')
    st.markdown(f"- **Valor Produto Total**: {fmt(total_produto)}")
    st.markdown(f"- **Total de IPI**: {fmt(total_ipi)}")
    st.markdown(f"- **Despesa Atual**: {fmt(desp_atual)}")
    st.markdown(f"- **CBS ({cbs_rate*100:.1f}%)**: {fmt(cbs_val)}")
    st.markdown(f"- **IBS ({ibs_rate*100:.1f}%)**: {fmt(ibs_val)}")
    st.markdown(f"- **CBS+IBS**: {fmt(cbs_ibs)}")
    st.markdown(f"- **Diferença**: {fmt(diff_val)}")
    st.markdown('---')

    # Detalhamento
    st.subheader('🗂 Detalhamento de Itens')
    cols = ['produto','ncm','valor_produto','Despesa Antes Reforma','CBS (%)','IBS (%)','Despesa Pós Reforma','Diferença Tributária']
    df_show = df_all[cols].round(2)
    gb = GridOptionsBuilder.from_dataframe(df_show)
    gb.configure_pagination(paginationAutoPageSize=False,paginationPageSize=10)
    AgGrid(df_show, gridOptions=gb.build(), fit_columns_on_grid_load=True, height=400)

    # CSV formatado
    csv_df = df_all.rename(columns={
        'produto':'Produto','ncm':'NCM','valor_produto':'Valor Produto',
        'Despesa Antes Reforma':'Despesa Antes Reforma','CBS (%)':'CBS (%)',
        'IBS (%)':'IBS (%)','Despesa Pós Reforma':'Despesa Pós Reforma',
        'Diferença Tributária':'Diferença Tributária'
    })
    for c in ['Valor Produto','Despesa Antes Reforma','CBS (%)','IBS (%)','Despesa Pós Reforma','Diferença Tributária']:
        csv_df[c] = csv_df[c].apply(fmt)
    csv_cols = ['Produto','NCM','Valor Produto','Despesa Antes Reforma','CBS (%)','IBS (%)','Despesa Pós Reforma','Diferença Tributária']
    csv_buffer = csv_df[csv_cols].to_csv(index=False, sep=';', encoding='utf-8-sig')
    st.download_button('📥 Baixar CSV Formatado', csv_buffer, file_name='relatorio_reforma.csv', mime='text/csv')

if __name__=='__main__':
    main()
