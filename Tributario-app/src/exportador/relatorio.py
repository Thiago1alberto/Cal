import pandas as pd
from datetime import datetime
import os

def gerar_excel(df: pd.DataFrame, pasta_saida: str = "data/outputs") -> str:
    """
    Gera um arquivo Excel com os dados tributários.
    Retorna o caminho do arquivo salvo.
    """
    if not os.path.exists(pasta_saida):
        os.makedirs(pasta_saida)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_arquivo = f"relatorio_tributos_{timestamp}.xlsx"
    caminho_completo = os.path.join(pasta_saida, nome_arquivo)

    df.to_excel(caminho_completo, index=False)

    return caminho_completo