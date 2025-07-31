"""
Sobre a Reforma Tributária - Informações sobre a RTI
"""
import streamlit as st

# Configuração da página
st.set_page_config(
    page_title="Sobre a Reforma Tributária",
    page_icon="🏛️",
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
</style>
""", unsafe_allow_html=True)

# Cabeçalho
st.markdown("""
<div class="main-header">
    <h1>🏛️ Sobre a Reforma Tributária</h1>
    <p>Entenda a PLP 39/2015 e as mudanças propostas</p>
</div>
""", unsafe_allow_html=True)

# O que é a RTI
st.markdown("## 📋 O que é a Reforma Tributária Integral (RTI)?")

st.markdown("""
<div class="info-card">
    <p>A Reforma Tributária Integral (RTI) é uma proposta de reestruturação do sistema tributário brasileiro, 
    formalizada através da <strong>PLP 39/2015</strong>, que visa simplificar e modernizar a cobrança de impostos no país.</p>
    
    <p>A proposta busca substituir múltiplos tributos por apenas dois novos impostos, eliminando a complexidade 
    e os efeitos cumulativos do sistema atual.</p>
</div>
""", unsafe_allow_html=True)

# Principais mudanças
st.markdown("## 🔄 Principais Mudanças Propostas")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### 🔴 EXTINÇÃO
    **Tributos que serão eliminados:**
    - **PIS** (Programa de Integração Social)
    - **COFINS** (Contribuição para Financiamento da Seguridade Social)
    - **ICMS** (Imposto sobre Circulação de Mercadorias e Serviços)
    - **ISS** (Imposto sobre Serviços)
    - **IPI** (Imposto sobre Produtos Industrializados) - parcial
    """)

with col2:
    st.markdown("""
    ### 🟢 CRIAÇÃO
    **Novos tributos unificados:**
    - **CBS** (Contribuição sobre Bens e Serviços)
      - Alíquota: ~0,9%
      - Substitui: PIS + COFINS
    - **IBS** (Imposto sobre Bens e Serviços)
      - Alíquota: ~26%
      - Substitui: ICMS + ISS
    """)

# Objetivos
st.markdown("## 🎯 Objetivos da Reforma")

objetivos = [
    "**Simplificação**: Reduzir de 5 para 2 tributos principais",
    "**Transparência**: Tornara tributação mais visível para o consumidor",
    "**Eficiência**: Eliminar efeitos cumulativos dos tributos",
    "**Competitividade**: Melhorar o ambiente de negócios brasileiro",
    "**Justiça Fiscal**: Distribuir a carga tributária de forma mais equitativa",
    "**Modernização**: Adequar o sistema às práticas internacionais"
]

for i, objetivo in enumerate(objetivos, 1):
    st.markdown(f"**{i}.** {objetivo}")

# Cronograma
st.markdown("## 📅 Cronograma Estimado")

st.markdown("""
<div class="warning-card">
    <h4>⏰ Fases de Implementação (Estimativas)</h4>
    <ul>
        <li><strong>2024-2025:</strong> Tramitação no Congresso Nacional</li>
        <li><strong>2026:</strong> Aprovação e regulamentação (previsão)</li>
        <li><strong>2027-2029:</strong> Implementação gradual por setores</li>
        <li><strong>2030+:</strong> Sistema totalmente implantado</li>
    </ul>
    <p><em>⚠️ Datas sujeitas a alterações conforme processo legislativo</em></p>
</div>
""", unsafe_allow_html=True)

# Impactos esperados
st.markdown("## 📊 Impactos Esperados")

tab1, tab2, tab3 = st.tabs(["🏢 Empresas", "👤 Consumidores", "🏛️ Governo"])

with tab1:
    st.markdown("""
    ### Para as Empresas:
    
    **✅ Pontos Positivos:**
    - Simplificação da apuração tributária
    - Redução de custos de compliance
    - Eliminação de efeitos cumulativos
    - Maior previsibilidade fiscal
    
    **⚠️ Desafios:**
    - Necessidade de adaptação dos sistemas
    - Treinamento das equipes
    - Possível aumento da carga em alguns setores
    """)

with tab2:
    st.markdown("""
    ### Para os Consumidores:
    
    **✅ Benefícios:**
    - Maior transparência nos preços
    - Tributos visíveis na nota fiscal
    - Possível redução de preços em alguns produtos
    
    **⚠️ Atenção:**
    - Possível aumento em alguns produtos/serviços
    - Período de adaptação do mercado
    """)

with tab3:
    st.markdown("""
    ### Para o Governo:
    
    **✅ Vantagens:**
    - Maior facilidade de arrecadação
    - Redução da sonegação
    - Melhor controle fiscal
    - Modernização do sistema
    
    **⚠️ Desafios:**
    - Coordenação entre União, Estados e Municípios
    - Implementação tecnológica
    - Capacitação dos servidores
    """)

# Metodologia desta aplicação
st.markdown("## 🧮 Metodologia desta Aplicação")

st.markdown("""
<div class="success-card">
    <h4>Como Calculamos o Impacto:</h4>
    
    <strong>1. Tributação Atual (Valores Reais):</strong>
    <ul>
        <li>PIS, COFINS, IPI, ICMS extraídos diretamente dos XMLs</li>
        <li>Não utilizamos alíquotas genéricas, mas sim os valores efetivamente pagos</li>
    </ul>
    
    <strong>2. Tributação RTI (Estimativa):</strong>
    <ul>
        <li>CBS: Valor do produto × 0,9% × (1 - % Redução conforme CST)</li>
        <li>IBS: Valor do produto × 26% × (1 - % Redução conforme CST)</li>
    </ul>
    
    <strong>3. Análise Comparativa:</strong>
    <ul>
        <li>Diferença = RTI - Tributação Atual</li>
        <li>Negativo = Economia | Positivo = Aumento</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# Avisos importantes
st.markdown("## ⚠️ Avisos Importantes")

st.markdown("""
<div class="warning-card">
    <h4>🚨 Leia Atentamente:</h4>
    <ul>
        <li><strong>Proposta em Tramitação:</strong> A PLP 39/2015 ainda está em discussão no Congresso</li>
        <li><strong>Valores Estimativos:</strong> Alíquotas e regras podem mudar durante o processo legislativo</li>
        <li><strong>Não Substitui Consultoria:</strong> Esta ferramenta oferece uma estimativa para planejamento</li>
        <li><strong>Consulte Profissionais:</strong> Para decisões definitivas, procure assessoria especializada</li>
        <li><strong>Mantenha-se Atualizado:</strong> Acompanhe as mudanças na proposta legislativa</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# Links úteis
st.markdown("## 🔗 Links Úteis")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### 📚 Fontes Oficiais:
    - [PLP 39/2015 - Câmara dos Deputados](https://www.camara.leg.br/)
    - [Receita Federal do Brasil](https://www.gov.br/receitafederal/)
    - [Ministério da Fazenda](https://www.gov.br/fazenda/)
    """)

with col2:
    st.markdown("""
    ### 🎓 Material de Estudo:
    - Consulte seu contador
    - Sindicatos e associações do setor
    - Cursos de atualização tributária
    """)

st.markdown("---")
st.markdown("*🏛️ Informações baseadas na proposta atual da PLP 39/2015 - Sujeitas a alterações*")
