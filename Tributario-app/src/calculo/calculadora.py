import pandas as pd

# Alíquotas simuladas (poderão vir de tabela futuramente)
ALIQUOTAS = {
    'PIS': 0.0065,     # 0,65%
    'COFINS': 0.03,    # 3%
    'ICMS': 0.18,      # 18% (padrão)
}

def calcular_tributos(df: pd.DataFrame) -> pd.DataFrame:
    """
    Recebe um DataFrame com itens da NF e calcula os principais tributos.
    """
    df_calc = df.copy()

    # Cálculos básicos
    df_calc['PIS'] = df_calc['valor_total'] * ALIQUOTAS['PIS']
    df_calc['COFINS'] = df_calc['valor_total'] * ALIQUOTAS['COFINS']
    df_calc['ICMS'] = df_calc['valor_total'] * ALIQUOTAS['ICMS']

    # Soma final (simples)
    df_calc['Total_Tributos'] = df_calc[['PIS', 'COFINS', 'ICMS']].sum(axis=1)

    return df_calc