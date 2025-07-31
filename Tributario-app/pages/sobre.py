"""
Página Sobre - Informações sobre a Reforma Tributária e a aplicação
"""
import streamlit as st

# Configuração da página
st.set_page_config(
    page_title="Sobre - Análise Tributária RTI",
    page_icon="ℹ️",
    layout="wide"
)

# CSS customizado
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .info-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #2a5298;
        margin: 1rem 0;
    }
    
    .warning-card {
        background: #fff3cd;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #ffc107;
        margin: 1rem 0;
    }
    
    .success-card {
        background: #d4edda;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #28a745;
        margin: 1rem 0;
    }
    
    .tech-card {
        background: #e3f2fd;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #2196f3;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Cabeçalho
st.markdown("""
<div class="main-header">
    <h1>ℹ️ Sobre a Análise Tributária RTI</h1>
    <p>Entenda a Reforma Tributária e como esta ferramenta pode ajudar sua empresa</p>
</div>
""", unsafe_allow_html=True)

# Abas para organizar o conteúdo
tab1, tab2, tab3, tab4 = st.tabs(["🏛️ Reforma Tributária", "💻 Sobre a Aplicação", "⚙️ Como Funciona", "📞 Contato"])

with tab1:
    st.markdown("## 🏛️ O que é a Reforma Tributária Integral (RTI)?")
    
    st.markdown("""
    <div class="info-card">
        <h4>📋 Definição</h4>
        <p>A Reforma Tributária Integral (RTI) é uma proposta de reestruturação do sistema tributário brasileiro, 
        formalizada através da <strong>PLP 39/2015</strong>, que visa simplificar e modernizar a cobrança de impostos no país.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Principais mudanças
    st.markdown("### 🔄 Principais Mudanças Propostas")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **🔴 EXTINÇÃO dos seguintes tributos:**
        - PIS (Programa de Integração Social)
        - COFINS (Contribuição para Financiamento da Seguridade Social)
        - ICMS (Imposto sobre Circulação de Mercadorias e Serviços)
        - ISS (Imposto sobre Serviços)
        - IPI (Imposto sobre Produtos Industrializados) - parcial
        """)
    
    with col2:
        st.markdown("""
        **🟢 CRIAÇÃO de novos tributos:**
        - **CBS** (Contribuição sobre Bens e Serviços) - ~0,9%
        - **IBS** (Imposto sobre Bens e Serviços) - ~26%
        - Manutenção do IPI para produtos específicos
        """)
    
    # Objetivos da reforma
    st.markdown("### 🎯 Objetivos da Reforma")
    
    objetivos = [
        "**Simplificação**: Reduzir a complexidade do sistema tributário",
        "**Transparência**: Tornar a tributação mais visível para o consumidor",
        "**Eficiência**: Eliminar efeitos cumulativos dos tributos",
        "**Competitividade**: Melhorar o ambiente de negócios",
        "**Justiça Fiscal**: Distribuir a carga tributária de forma mais equitativa"
    ]
    
    for objetivo in objetivos:
        st.markdown(f"✅ {objetivo}")
    
    # Cronograma (estimado)
    st.markdown("### 📅 Cronograma Estimado")
    
    st.markdown("""
    - **2024-2025**: Tramitação no Congresso Nacional
    - **2026**: Aprovação e regulamentação (previsão)
    - **2027-2030**: Implementação gradual
    - **2030+**: Sistema totalmente implantado
    
    ⚠️ **Atenção**: Datas sujeitas a alterações conforme processo legislativo
    """)

with tab2:
    st.markdown("## 💻 Sobre Esta Aplicação")
    
    st.markdown("""
    <div class="success-card">
        <h4>🎯 Objetivo da Ferramenta</h4>
        <p>Esta aplicação foi desenvolvida para permitir que empresas, contadores e gestores possam:</p>
        <ul>
            <li>📊 Analisar o impacto da RTI em suas operações</li>
            <li>💰 Comparar a carga tributária atual vs proposta</li>
            <li>📈 Identificar potenciais economias ou aumentos</li>
            <li>📋 Gerar relatórios detalhados para tomada de decisão</li>
            <li>🔍 Processar múltiplas notas fiscais simultaneamente</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Tecnologias utilizadas
    st.markdown("### 🛠️ Tecnologias Utilizadas")
    
    st.markdown("""
    <div class="tech-card">
        <h4>💻 Stack Tecnológico</h4>
        <ul>
            <li><strong>Python 3.8+</strong>: Linguagem principal</li>
            <li><strong>Streamlit</strong>: Interface web interativa</li>
            <li><strong>Pandas</strong>: Manipulação de dados</li>
            <li><strong>Plotly</strong>: Visualizações interativas</li>
            <li><strong>lxml</strong>: Parser de XML otimizado</li>
            <li><strong>Pydantic</strong>: Validação de dados</li>
            <li><strong>OpenPyXL</strong>: Manipulação de arquivos Excel</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Arquitetura
    st.markdown("### 🏗️ Arquitetura do Sistema")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **📁 Estrutura Modular:**
        - `src/models/`: Modelos de dados
        - `src/parser/`: Processamento de XML
        - `src/calculo/`: Engine de cálculos
        - `src/util/`: Utilitários e formatação
        - `pages/`: Páginas da aplicação
        """)
    
    with col2:
        st.markdown("""
        **🔧 Características:**
        - ✅ Código modular e testável
        - ✅ Validação robusta de dados
        - ✅ Interface responsiva
        - ✅ Processamento em lote
        - ✅ Exportação de relatórios
        """)

with tab3:
    st.markdown("## ⚙️ Como Funciona a Análise")
    
    # Fluxo do processo
    st.markdown("### 🔄 Fluxo do Processo")
    
    steps = [
        ("1️⃣", "**Upload da Tabela CST**", "Carregue a planilha com configurações de CST e reduções"),
        ("2️⃣", "**Upload dos XMLs**", "Faça upload dos arquivos XML das notas fiscais"),
        ("3️⃣", "**Extração de Dados**", "Sistema extrai valores reais dos tributos dos XMLs"),
        ("4️⃣", "**Cálculo RTI**", "Aplica regras da nova legislação aos dados extraídos"),
        ("5️⃣", "**Comparação**", "Compara tributação atual vs RTI para cada item"),
        ("6️⃣", "**Relatórios**", "Gera visualizações e relatórios detalhados")
    ]
    
    for emoji, title, desc in steps:
        st.markdown(f"""
        <div class="info-card">
            <h4>{emoji} {title}</h4>
            <p>{desc}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Metodologia
    st.markdown("### 🧮 Metodologia de Cálculo")
    
    st.markdown("""
    **Tributação Atual (extraída do XML):**
    - PIS: Valor real da nota fiscal
    - COFINS: Valor real da nota fiscal  
    - IPI: Valor real da nota fiscal
    - ICMS: Valor real da nota fiscal
    
    **Tributação RTI (calculada):**
    - CBS: Valor do produto × Alíquota CBS × (1 - % Redução)
    - IBS: Valor do produto × Alíquota IBS × (1 - % Redução)
    
    **Reduções aplicadas conforme CST:**
    - Produtos monofásicos
    - Reduções específicas por NCM
    - Diferimentos previstos
    """)

with tab4:
    st.markdown("## 📞 Informações de Contato e Suporte")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="info-card">
            <h4>👨‍💻 Desenvolvedor</h4>
            <p>Esta aplicação foi desenvolvida utilizando as melhores práticas de desenvolvimento Python, 
            com foco em automação tributária e facilidade de uso para profissionais da área fiscal e contábil.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        **🎯 Público-Alvo:**
        - Contadores e escritórios contábeis
        - Gestores fiscais de empresas
        - Consultores tributários
        - Analistas financeiros
        """)
    
    with col2:
        st.markdown("""
        <div class="success-card">
            <h4>📧 Suporte</h4>
            <p>Para dúvidas, sugestões ou reportar problemas:</p>
            <ul>
                <li>📊 Análises personalizadas</li>
                <li>🛠️ Customizações específicas</li>
                <li>📈 Implementação empresarial</li>
                <li>🎓 Treinamentos</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Versão e atualizações
    st.markdown("---")
    st.markdown("### 📋 Informações da Versão")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Versão", "1.0.0")
    
    with col2:
        st.metric("Última Atualização", "31/07/2025")
    
    with col3:
        st.metric("Notas Processadas", "Ilimitado*")
    
    st.caption("*Limitado apenas pelos recursos do sistema")

# Avisos legais
st.markdown("---")
st.markdown("### ⚠️ Avisos Legais e Disclaimer")

st.markdown("""
<div class="warning-card">
    <h4>🚨 Importante - Leia Atentamente</h4>
    <ul>
        <li><strong>Proposta em Tramitação</strong>: A PLP 39/2015 ainda está em discussão no Congresso Nacional</li>
        <li><strong>Valores Sujeitos a Alteração</strong>: Alíquotas e regras podem mudar durante o processo legislativo</li>
        <li><strong>Simulação Estimativa</strong>: Esta ferramenta oferece uma estimativa baseada na proposta atual</li>
        <li><strong>Não Substitui Assessoria</strong>: Recomenda-se consultar profissionais especializados para decisões definitivas</li>
        <li><strong>Responsabilidade</strong>: O uso desta ferramenta é de inteira responsabilidade do usuário</li>
    </ul>
</div>
""", unsafe_allow_html=True)

st.markdown("---")
st.markdown("*Desenvolvido com ❤️ para profissionais da área tributária*")
