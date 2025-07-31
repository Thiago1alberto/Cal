
import xml.etree.ElementTree as ET
import pandas as pd


def ler_xml_universal(caminho_arquivo: str) -> pd.DataFrame:
    """
    Lê qualquer XML (tratando namespaces) e devolve um DataFrame com:
      - path: caminho hierárquico até o elemento (tag1/tag2/...)
      - tag: nome da tag (sem namespace)
      - attributes: dict de atributos
      - text: conteúdo de texto (ou None)
    """
    tree = ET.parse(caminho_arquivo)
    root = tree.getroot()
    registros = []

    def clean_tag(tag: str) -> str:
        # Remove namespace: {uri}tag -> tag
        return tag.split('}', 1)[-1] if '}' in tag else tag

    def percorrer(elem, caminho=""):
        tag = clean_tag(elem.tag)
        novo_path = f"{caminho}/{tag}" if caminho else tag
        registros.append({
            "path":       novo_path,
            "tag":        tag,
            "attributes": elem.attrib or {},
            "text":       elem.text.strip() if elem.text and elem.text.strip() else None
        })
        for filho in elem:
            percorrer(filho, novo_path)

    percorrer(root)
    return pd.DataFrame(registros)