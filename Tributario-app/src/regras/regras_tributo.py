def obter_regra_por_cst(cst: str) -> dict:
    """
    Retorna as regras tributárias aplicáveis com base no CST informado.
    Pode ser expandido com tabelas externas (como a CST que você tem).
    """
    regras = {
        '000': {'PIS': 0.0065, 'COFINS': 0.03, 'ICMS': 0.18},
        '010': {'PIS': 0.0065, 'COFINS': 0.03, 'ICMS': 0.12},
        '020': {'PIS': 0.0065, 'COFINS': 0.03, 'ICMS': 0.07},
        '060': {'PIS': 0.0, 'COFINS': 0.0, 'ICMS': 0.0},  # Alíquota zero
        # ... incluir mais CSTs conforme necessário
    }

    return regras.get(cst, {'PIS': 0.0065, 'COFINS': 0.03, 'ICMS': 0.18})  # padrão