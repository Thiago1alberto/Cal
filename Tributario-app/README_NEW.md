# 🏛️ Análise Tributária - Reforma Tributária (RTI)

## 📋 Descrição

Aplicação web desenvolvida em Streamlit para análise comparativa entre a tributação atual e a proposta da Reforma Tributária Integral (RTI) conforme PLP 39/2015.

### 🎯 Principais Funcionalidades

- **📤 Upload Múltiplo**: Aceita múltiplos arquivos XML de NF-e/NFC-e
- **🔍 Validação Robusta**: Validação automática de estrutura dos XMLs
- **📊 Análise Comparativa**: Comparação detalhada entre tributação atual vs RTI
- **💰 Cálculos Precisos**: Extração de valores reais dos XMLs (não simulados)
- **📈 Visualizações**: Gráficos interativos com Plotly
- **💾 Relatórios**: Export para CSV e resumo executivo
- **⚙️ Configurável**: Alíquotas ajustáveis da RTI

### 🏗️ Arquitetura

```
Tributario-app/
├── src/
│   ├── models/          # Modelos de dados (Pydantic)
│   ├── parser/          # Parser robusto de XML
│   ├── calculo/         # Calculadora tributária
│   └── util/           # Utilitários e formatadores
├── .streamlit/         # Configurações do Streamlit
├── app_new.py         # Aplicação principal moderna
├── requirements.txt   # Dependências
└── README.md         # Este arquivo
```

## 🚀 Como Usar

### 1. Instalação

```bash
# Clone o repositório
git clone [seu-repositório]
cd Tributario-app

# Instale as dependências
pip install -r requirements.txt
```

### 2. Execução

```bash
# Execute a aplicação
streamlit run app_new.py
```

### 3. Uso da Aplicação

1. **📊 Carregue a Tabela CST**: Upload do arquivo Excel com classificações tributárias
2. **📄 Carregue XMLs**: Upload de um ou múltiplos arquivos XML de NF-e/NFC-e
3. **🚀 Processe**: Clique em "Processar Análise Tributária"
4. **📈 Analise**: Visualize os resultados comparativos
5. **💾 Exporte**: Download de relatórios em CSV ou resumo executivo

## 📊 Funcionalidades Principais

### Extração de Dados
- ✅ Valor total dos produtos
- ✅ Total de PIS (valores reais do XML)
- ✅ Total de COFINS (valores reais do XML)
- ✅ Total de IPI (valores reais do XML)
- ✅ Total de ICMS (valores reais do XML)

### Cálculos RTI
- ✅ CBS (Contribuição sobre Bens e Serviços)
- ✅ IBS (Imposto sobre Bens e Serviços)
- ✅ Reduções por CST
- ✅ Isenções e monofásicas

### Relatórios
- ✅ Resumo consolidado
- ✅ Comparação "Antes vs Depois"
- ✅ Detalhamento por item
- ✅ Gráficos interativos
- ✅ Mensagens de economia/aumento

## 🛠️ Tecnologias Utilizadas

- **Python 3.8+**
- **Streamlit** - Interface web
- **Pandas** - Manipulação de dados
- **Plotly** - Visualizações interativas
- **lxml/xmltodict** - Parsing de XML
- **Pydantic** - Validação de dados
- **OpenPyXL** - Leitura de Excel

## ⚙️ Configurações Avançadas

### Alíquotas RTI (Configuráveis)
- **CBS**: 0.9% (padrão)
- **IBS**: 26% (padrão - valor médio estimado)

### Estrutura CST Suportada
- ✅ Exigência de tributação
- ✅ Regimes monofásicos
- ✅ Reduções de alíquota
- ✅ Diferimentos
- ✅ Percentuais de redução CBS/IBS

## 🔧 Melhorias Implementadas

### Em relação ao código anterior:
1. **Arquitetura Modular**: Separação clara de responsabilidades
2. **Parser Robusto**: Suporte a diferentes versões de NF-e
3. **Validação Avançada**: Verificação de estrutura XML
4. **Interface Moderna**: Design responsivo e intuitivo
5. **Cálculos Precisos**: Extração de valores reais dos XMLs
6. **Error Handling**: Tratamento abrangente de erros
7. **Performance**: Processamento eficiente de múltiplos arquivos

## 📝 Notas Importantes

- **⚠️ Aviso Legal**: Esta análise é baseada na proposta atual da PLP 39/2015. Os valores e alíquotas podem ser alterados durante o processo legislativo.
- **🔒 Segurança**: Recomenda-se implementar autenticação para uso em produção
- **📊 Dados**: A aplicação extrai valores reais dos XMLs, não simulações baseadas em tabelas externas

## 🤝 Contribuição

Para contribuir com o projeto:
1. Fork o repositório
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para detalhes.

## 📞 Suporte

Para dúvidas ou sugestões, entre em contato através dos issues do GitHub.
