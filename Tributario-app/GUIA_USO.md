# 🎯 Guia de Uso - Análise Tributária RTI

## 📋 Visão Geral

Esta aplicação permite comparar a tributação atual de Notas Fiscais Eletrônicas (NF-e) com a proposta da Reforma Tributária Integral (RTI) conforme PLP 39/2015.

## 🚀 Como Executar

### 1. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 2. Executar a Aplicação
```bash
streamlit run app_new.py
```

### 3. Acessar no Navegador
A aplicação abrirá automaticamente em: `http://localhost:8501`

## 📁 Arquivos Necessários

### 1. 📊 Tabela de CST (Excel)
- **Arquivo**: `Tabela de CST e CLASSIFICAÇÃO TRIBUTARIA.xlsx`
- **Formato**: Excel (.xlsx ou .xls)
- **Colunas obrigatórias**:
  - `CST`: Código de Situação Tributária
  - `Exige Trib`: Se exige tributação (SIM/NÃO)
  - `Monofásica`: Se é monofásica (SIM/NÃO)
  - `Red. Alíq`: Se tem redução de alíquota (SIM/NÃO)
  - `Diferimento`: Se tem diferimento (SIM/NÃO)
  - `% Red. CBS`: Percentual de redução CBS (0-100%)
  - `% Red. IBS`: Percentual de redução IBS (0-100%)

### 2. 📄 Notas Fiscais (XML)
- **Formato**: XML de NF-e ou NFC-e
- **Quantidade**: Suporta múltiplos arquivos
- **Validação**: Automática para estrutura de NF-e

## 🔧 Passo a Passo de Uso

### Etapa 1: Carregar Tabela CST
1. Clique em "**📊 Tabela de CST**"
2. Selecione o arquivo Excel
3. Aguarde o processamento
4. Verifique se aparece "✅ Tabela CST carregada com sucesso!"

### Etapa 2: Carregar XMLs
1. Clique em "**📄 Notas Fiscais (XML)**"
2. Selecione um ou múltiplos arquivos XML
3. Verifique se os arquivos são válidos

### Etapa 3: Processar Análise
1. Clique no botão "**🚀 Processar Análise Tributária**"
2. Aguarde o processamento
3. Visualize os resultados

## 📊 Resultados da Análise

### 📈 Resumo Consolidado
- **💰 Valor Total Produtos**: Soma de todos os produtos
- **🏛️ Tributação Atual**: Total de PIS + COFINS + IPI + ICMS
- **🆕 Tributação RTI**: Total de CBS + IBS
- **📈 Diferença**: Economia ou aumento tributário

### 🔍 Comparação Detalhada
- **Gráficos de pizza** comparando tributos atuais vs RTI
- **Breakdown por tipo de tributo**
- **Visualizações interativas**

### 📋 Detalhamento por Item
- **Tabela completa** com todos os itens das notas
- **Cálculos individuais** por produto
- **Percentuais de economia** por item
- **Exportação em CSV**

## ⚙️ Configurações Avançadas

### Alíquotas RTI (Sidebar)
- **CBS**: Padrão 0.9% (ajustável 0-5%)
- **IBS**: Padrão 26% (ajustável 0-30%)

### Recálculo
- Use o botão "**🔄 Reprocessar Cálculos**" após alterar alíquotas

## 📥 Relatórios Disponíveis

### 1. 📄 Relatório CSV
- **Conteúdo**: Detalhamento completo por item
- **Formato**: CSV com separador `;`
- **Uso**: Análise em Excel/Planilhas

### 2. 📊 Resumo Executivo
- **Conteúdo**: Análise consolidada em texto
- **Formato**: TXT
- **Uso**: Apresentações e relatórios gerenciais

## 🔍 Exemplos de Mensagens

### ✅ Sucesso
- "✅ Tabela CST carregada com sucesso! (150 registros)"
- "✅ 3 nota(s) fiscal(is) processada(s) com sucesso!"

### 🎉 Economia
- "🎉 **ECONOMIA de R$ 1.234,56** (15,30%)"

### ⚠️ Aumento
- "⚠️ **AUMENTO de R$ 567,89** (8,45%)"

### ➡️ Sem Alteração
- "➡️ **SEM ALTERAÇÃO** na carga tributária"

## 🚨 Possíveis Problemas e Soluções

### ❌ "Arquivo não é uma NF-e válida"
**Causa**: XML não contém estrutura de NF-e
**Solução**: Verifique se o arquivo é realmente um XML de NF-e

### ❌ "Colunas obrigatórias não encontradas"
**Causa**: Planilha CST sem colunas necessárias
**Solução**: Certifique-se que a planilha tem todas as colunas obrigatórias

### ❌ "Erro ao processar XML"
**Causa**: XML corrompido ou com estrutura inválida
**Solução**: Valide o XML ou obtenha uma nova cópia

### ⚠️ "Carregue primeiro a tabela de CST"
**Causa**: Tentativa de processar XMLs sem carregar tabela CST
**Solução**: Carregue a tabela CST antes dos XMLs

## 📝 Notas Importantes

### ⚠️ Aviso Legal
Esta análise é baseada na **proposta atual da PLP 39/2015**. Os valores e alíquotas podem ser alterados durante o processo legislativo.

### 🔒 Segurança
- Os arquivos são processados localmente
- Nenhum dado é enviado para servidores externos
- Para uso em produção, considere implementar autenticação

### 📊 Precisão dos Cálculos
- A aplicação extrai **valores reais** dos XMLs
- Não utiliza simulações baseadas em tabelas externas
- Considera CSTs, isenções e regimes especiais

## 🛠️ Suporte Técnico

### Logs de Debug
Para ativar logs detalhados, edite o arquivo `app_new.py` e defina:
```python
parser.set_debug(True)
```

### Teste da Aplicação
Execute o script de teste:
```bash
python test_app.py
```

### Estrutura de Arquivos
```
Tributario-app/
├── app_new.py              # Aplicação principal
├── test_app.py             # Testes
├── requirements.txt        # Dependências
├── README_NEW.md          # Documentação técnica
├── GUIA_USO.md            # Este guia
├── src/
│   ├── models/            # Modelos de dados
│   ├── parser/            # Parser de XML
│   ├── calculo/           # Calculadora tributária
│   └── util/              # Utilitários
└── .streamlit/
    └── config.toml        # Configurações do Streamlit
```

## 📞 Contato

Para dúvidas, sugestões ou problemas:
- Abra uma issue no repositório
- Entre em contato com a equipe de desenvolvimento

---

**Desenvolvido para análise de impacto da Reforma Tributária (RTI)**
*Baseado na PLP 39/2015 - Sujeito a alterações conforme evolução legislativa*
