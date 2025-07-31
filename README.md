# 📊 Análise Tributária - Reforma Tributária Integral (RTI)

Sistema para análise comparativa entre a tributação atual e a proposta da **PLP 39/2015** (Reforma Tributária Integral).

## 📁 Estrutura do Projeto

```
Cal/
├── 📱 Tributario-app/          # Aplicação principal
│   ├── app_new.py              # Interface Streamlit
│   ├── src/                    # Código fonte modular
│   │   ├── models/             # Modelos de dados
│   │   ├── parser/             # Processamento de XML
│   │   ├── calculo/            # Engine de cálculos
│   │   └── util/               # Utilitários
│   ├── pages/                  # Páginas da aplicação
│   │   ├── Manual_de_Uso.py    # Guia do usuário
│   │   └── Sobre_a_Reforma.py  # Informações da RTI
│   └── .streamlit/             # Configurações do Streamlit
│
├── 📊 dados/                   # Arquivos de dados
│   └── Tabela de CST e CLASSIFICAÇÃO TRIBUTARIA.xlsx
│
├── 📋 docs/                    # Documentação
│   └── Nota_Tecnica_Correcao_Tributaria.txt
│
├── 🐍 .venv/                   # Ambiente virtual Python
└── 📝 README.md                # Este arquivo
```

## 🚀 Como Executar

### 1. Ative o ambiente virtual
```bash
# Windows
.venv\Scripts\Activate.ps1

# Linux/Mac
source .venv/bin/activate
```

### 2. Execute a aplicação
```bash
streamlit run Tributario-app/app_new.py
```

### 3. Acesse no navegador
```
http://localhost:8501
```

## 📖 Como Usar

1. **📊 Carregue a Tabela CST**: Use o arquivo em `dados/Tabela de CST e CLASSIFICAÇÃO TRIBUTARIA.xlsx`
2. **📄 Upload XMLs**: Carregue os arquivos XML das notas fiscais
3. **🚀 Processe**: Clique em "Processar Análise Tributária"
4. **📈 Analise**: Veja os resultados comparativos

## 🎯 Funcionalidades

- ✅ **Extração de dados reais** dos XMLs das NF-e/NFC-e
- ✅ **Cálculo comparativo** entre tributação atual e RTI
- ✅ **Processamento em lote** de múltiplas notas
- ✅ **Visualizações interativas** com gráficos
- ✅ **Relatórios exportáveis** em CSV e texto
- ✅ **Interface intuitiva** com Streamlit

## 📋 Requisitos

- **Python 3.8+**
- **Bibliotecas**: Streamlit, pandas, plotly, lxml, pydantic
- **Arquivos**: Tabela CST (Excel) + XMLs das notas fiscais

## ⚠️ Importante

Esta ferramenta oferece uma **estimativa** baseada na proposta atual da PLP 39/2015. Os valores e regras podem mudar durante o processo legislativo. **Consulte sempre um profissional especializado** para decisões definitivas.

## 📞 Suporte

Para dúvidas sobre o uso da aplicação, consulte:
- 📖 **Manual de Uso** (dentro da aplicação)
- 🏛️ **Sobre a Reforma** (informações detalhadas da RTI)

---
*Desenvolvido para facilitar a análise do impacto da Reforma Tributária Integral*
