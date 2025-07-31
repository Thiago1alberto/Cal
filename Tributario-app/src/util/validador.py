import xmltodict

def validar_estrutura_xml(file) -> bool:
    """
    Valida se o XML contém a estrutura básica esperada de uma NF-e.
    Retorna True se válido, lança exceção se inválido.
    """
    try:
        doc = xmltodict.parse(file.read())
        file.seek(0)  # Resetar ponteiro do arquivo para leitura posterior

        # Checagem mínima da estrutura esperada
        if 'nfeProc' not in doc:
            raise ValueError("Tag <nfeProc> não encontrada. O arquivo pode não ser uma NF-e válida.")
        if 'NFe' not in doc['nfeProc']:
            raise ValueError("Tag <NFe> ausente dentro de <nfeProc>.")
        if 'infNFe' not in doc['nfeProc']['NFe']:
            raise ValueError("Tag <infNFe> ausente.")

        return True

    except Exception as e:
        raise ValueError(f"Erro na validação do XML: {e}")
    