"""
Manual de Uso - Como usar a Análise Tributária RTI
"""
import streamlit as st

# Configuração da página
st.set_page_config(
    page_title="Manual de Uso - RTI",
    page_icon="📖",
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
    
    .step-card {
        background: #ffffff;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .tip-card {
        background: #e8f5e8;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    
    .warning-card {
        background: #fff3cd;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #ffc107;
        margin: 1rem 0;
    }
    
    .important-card {
        background: #f8d7da;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #dc3545;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Cabeçalho
st.markdown("""
<div class="main-header">
    <h1>📖 Manual de Uso</h1>
    <p>Guia prático para usar a Análise Tributária RTI</p>
</div>
""", unsafe_allow_html=True)

# Preparação
st.markdown("## 🎯 Antes de Começar")

st.markdown("""
<div class="tip-card">
    <h4>📋 O que você precisa ter em mãos:</h4>
    <ul>
        <li><strong>📊 Planilha de CST</strong>: arquivo Excel em <code>../dados/</code></li>
        <li><strong>📄 Arquivos XML</strong>: das notas fiscais que deseja analisar (NF-e ou NFC-e)</li>
        <li><strong>🌐 Navegador</strong>: Chrome, Firefox, Edge ou Safari atualizado</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# Passo a passo
st.markdown("## 🚀 Passo a Passo")

# Passo 1
st.markdown("""
<div class="step-card">
    <h3>1️⃣ Carregue a Tabela de CST</h3>
    <p><strong>Local:</strong> Seção "📊 Tabela de CST" na página principal</p>
    <p><strong>Arquivo:</strong> <code>dados/Tabela de CST e CLASSIFICAÇÃO TRIBUTARIA.xlsx</code></p>
    <p><strong>O que fazer:</strong></p>
    <ul>
        <li>Clique em "Browse files" ou arraste o arquivo Excel</li>
        <li>Navegue até a pasta <strong>dados</strong> e selecione a tabela</li>
        <li>Aguarde a mensagem "✅ Tabela CST carregada com sucesso!"</li>
    </ul>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="tip-card">
    <strong>💡 Dica:</strong> A tabela só precisa ser carregada uma vez por sessão. 
    Você pode processar várias notas fiscais sem recarregar a tabela.
</div>
""", unsafe_allow_html=True)

# Resto do conteúdo permanece igual
st.markdown("""
<div class="step-card">
    <h3>2️⃣ Carregue as Notas Fiscais</h3>
    <p><strong>Local:</strong> Seção "📄 Notas Fiscais (XML)" na página principal</p>
    <p><strong>O que fazer:</strong></p>
    <ul>
        <li>Clique em "Browse files" ou arraste os arquivos XML</li>
        <li>Selecione um ou múltiplos arquivos XML de NF-e/NFC-e</li>
        <li>Confirme que os arquivos aparecem na lista</li>
    </ul>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="tip-card">
    <strong>💡 Dica:</strong> Você pode carregar várias notas fiscais de uma vez! 
    Segure Ctrl (Windows) ou Cmd (Mac) para selecionar múltiplos arquivos.
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="step-card">
    <h3>3️⃣ Processe a Análise</h3>
    <p><strong>Local:</strong> Botão azul "🚀 Processar Análise Tributária"</p>
    <p><strong>O que fazer:</strong></p>
    <ul>
        <li>Clique no botão após carregar a tabela CST e os XMLs</li>
        <li>Aguarde a barra de progresso completar</li>
        <li>Veja a mensagem de confirmação do processamento</li>
    </ul>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="warning-card">
    <strong>⚠️ Atenção:</strong> O processamento pode demorar alguns segundos dependendo 
    da quantidade de notas fiscais e itens.
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="step-card">
    <h3>4️⃣ Analise os Resultados</h3>
    <p><strong>Local:</strong> Seção "📈 Resultados da Análise" (aparece após processamento)</p>
    <p><strong>O que você verá:</strong></p>
    <ul>
        <li><strong>📊 Resumo Consolidado:</strong> métricas gerais e diferença total</li>
        <li><strong>🔍 Comparação Detalhada:</strong> tributos atuais vs RTI</li>
        <li><strong>📋 Detalhamento por Item:</strong> tabela com todos os produtos</li>
        <li><strong>💾 Download de Relatórios:</strong> opções de exportação</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# Entendendo os resultados
st.markdown("## 📊 Entendendo os Resultados")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### 🟢 Economia (Verde)
    - **Significado**: A RTI resultará em MENOS tributos
    - **Cor**: Verde/positivo
    - **Símbolo**: 🎉
    - **Exemplo**: "ECONOMIA de R$ 1.500 (15%)"
    """)

with col2:
    st.markdown("""
    ### 🔴 Aumento (Vermelho)  
    - **Significado**: A RTI resultará em MAIS tributos
    - **Cor**: Vermelho/negativo
    - **Símbolo**: ⚠️
    - **Exemplo**: "AUMENTO de R$ 800 (8%)"
    """)

st.markdown("## 💡 Estrutura do Projeto")

st.markdown("""
<div class="tip-card">
    <h4>📁 Localização dos Arquivos:</h4>
    <ul>
        <li><strong>📊 Tabela CST:</strong> <code>../dados/Tabela de CST e CLASSIFICAÇÃO TRIBUTARIA.xlsx</code></li>
        <li><strong>📋 Documentação:</strong> <code>../docs/Nota_Tecnica_Correcao_Tributaria.txt</code></li>
        <li><strong>📱 Aplicação:</strong> <code>Tributario-app/</code> (pasta atual)</li>
        <li><strong>💾 Saídas:</strong> <code>data/outputs/</code> (relatórios gerados)</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# Informações finais
st.markdown("---")
st.markdown("### ℹ️ Informações Importantes")

st.markdown("""
<div class="important-card">
    <strong>⚠️ Lembre-se:</strong>
    <ul>
        <li>Esta é uma simulação baseada na proposta atual da PLP 39/2015</li>
        <li>Valores e regras podem mudar durante o processo legislativo</li>
        <li>Consulte sempre um profissional especializado para decisões definitivas</li>
        <li>Os arquivos estão organizados na nova estrutura de pastas</li>
    </ul>
</div>
""", unsafe_allow_html=True)

st.markdown("---")
st.markdown("*📖 Manual atualizado com a nova estrutura organizacional - Versão 1.1*")