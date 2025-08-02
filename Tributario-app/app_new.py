"""
Aplicação Streamlit para Análise Tributária - RTI vs Legislação Atual
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io
import base64
from decimal import Decimal
from typing import List, Dict, Any
import os

# Imports locais
from src.parser.nf_parser import NFParser, NFParserError
from src.calculo.calculadora_rti import CalculadoraTributaria
from src.models import ConfigTributacao, NotaFiscal, CalculoComparativo
from src.util.formatters import (
    format_currency, format_percentage, get_economy_message, 
    generate_summary_stats, validate_xml_nfe
)


# Configuração da página
st.set_page_config(
    page_title="Análise Tributária RTI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }
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
    
    .metric-container {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #2a5298;
    }
    
    .economy-positive {
        background: linear-gradient(90deg, #27ae60 0%, #2ecc71 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
    }
    
    .economy-negative {
        background: linear-gradient(90deg, #e74c3c 0%, #c0392b 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
    }
    
    .info-box {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #17a2b8;
        margin: 1rem 0;
    }
    
    .stButton > button {
        background: linear-gradient(90deg, #2a5298 0%, #1e3c72 100%);
        color: white;
        border-radius: 8px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


class TributaryApp:
    """Classe principal da aplicação tributária"""
    
    def __init__(self):
        self.parser = NFParser()
        self.calculator = None
        self.notas_processadas: List[NotaFiscal] = []
        self.comparativos: List[CalculoComparativo] = []
        
        # Inicializa session state
        if 'processed_files' not in st.session_state:
            st.session_state.processed_files = []
        if 'cst_loaded' not in st.session_state:
            st.session_state.cst_loaded = False
        if 'df_cst' not in st.session_state:
            st.session_state.df_cst = None
            
        # Tenta recuperar calculadora se dados estão na sessão
        if st.session_state.cst_loaded and st.session_state.df_cst is not None and self.calculator is None:
            try:
                config = ConfigTributacao()
                self.calculator = CalculadoraTributaria(config)
                self.calculator.carregar_tabela_cst(st.session_state.df_cst)
                st.sidebar.success("🔄 Calculadora recuperada da sessão!")
            except Exception as e:
                st.sidebar.error(f"❌ Erro ao recuperar calculadora: {e}")
                st.session_state.cst_loaded = False
    
    def render_header(self):
        """Renderiza o cabeçalho da aplicação"""
        st.markdown("""
        <div class="main-header">
            <h1>🏛️ Análise Tributária - Reforma Tributária (RTI)</h1>
            <p>Comparação entre Tributação Atual e Nova Legislação (PLP 39/2015)</p>
        </div>
        """, unsafe_allow_html=True)
    
    def render_plp_info(self):
        """Renderiza informações sobre a PLP"""
        with st.expander("📋 Informações sobre a PLP 39/2015 - Reforma Tributária", expanded=False):
            st.markdown("""
            ### 🎯 Principais Mudanças da Reforma Tributária
            
            **Substituições Propostas:**
            - **PIS/COFINS** → **CBS** (Contribuição sobre Bens e Serviços)
            - **ICMS/ISS** → **IBS** (Imposto sobre Bens e Serviços)
            
            **Objetivos:**
            - ✅ Simplificação do sistema tributário
            - ✅ Redução da burocracia fiscal
            - ✅ Eliminação de efeitos cumulativos
            - ✅ Maior transparência na tributação
            
            **Alíquotas de Referência:**
            - **CBS**: ~0,9% (substitui PIS/COFINS)
            - **IBS**: ~26% (substitui ICMS/ISS) - *Valor médio estimado*
            
            **⚠️ Importante:** Esta análise é baseada na proposta atual da PLP 39/2015. 
            Os valores e alíquotas podem ser alterados durante o processo legislativo.
            """)
    
    def load_cst_table(self, uploaded_file) -> bool:
        """Carrega e processa a tabela de CST"""
        try:
            # Lê o arquivo Excel
            df_raw = pd.read_excel(uploaded_file, header=None)
            
            # Encontra a linha do cabeçalho (onde está "CST")
            header_row = None
            for idx, row in df_raw.iterrows():
                if any('CST' in str(cell) for cell in row if cell is not None):
                    header_row = idx
                    break
            
            if header_row is None:
                st.error("Não foi possível encontrar o cabeçalho 'CST' na planilha")
                return False
            
            # Lê novamente com o cabeçalho correto
            df_cst = pd.read_excel(uploaded_file, header=header_row)
            
            # Remove colunas unnamed
            df_cst = df_cst.loc[:, ~df_cst.columns.str.contains('^Unnamed')]
            
            # Limpa nomes das colunas
            df_cst.columns = df_cst.columns.str.strip()
            
            # Verifica colunas essenciais
            required_cols = ['CST']
            missing_cols = [col for col in required_cols if col not in df_cst.columns]
            
            if missing_cols:
                st.error(f"Colunas obrigatórias não encontradas: {missing_cols}")
                return False
            
            # Processa dados
            df_cst = df_cst.dropna(subset=['CST'])
            
            # Padroniza coluna CST
            df_cst['CST'] = df_cst['CST'].astype(str).str.strip()
            
            # Converte flags booleanos
            bool_columns = ['Exige Trib', 'Monofásica', 'Red. Alíq', 'Diferimento']
            for col in bool_columns:
                if col in df_cst.columns:
                    df_cst[col] = df_cst[col].astype(str).str.upper().map({
                        'SIM': True, 'NÃO': False, 'NAO': False, 'TRUE': True, 'FALSE': False
                    }).fillna(False)
                else:
                    df_cst[col] = False
            
            # Processa porcentagens de redução
            pct_columns = ['% Red. CBS', '% Red. IBS']
            for col in pct_columns:
                if col in df_cst.columns:
                    df_cst[col] = (df_cst[col].astype(str)
                                  .str.replace('%', '')
                                  .str.replace(',', '.')
                                  .apply(lambda x: float(x) / 100 if x and x != 'nan' else 0))
                else:
                    df_cst[col] = 0.0
            
            # Inicializa calculadora
            config = ConfigTributacao()
            self.calculator = CalculadoraTributaria(config)
            self.calculator.carregar_tabela_cst(df_cst)
            
            # Salva na sessão para recuperar se necessário
            st.session_state.df_cst = df_cst
            st.session_state.cst_loaded = True
            
            # Mostra preview dos dados
            st.success(f"✅ Tabela CST carregada com sucesso! ({len(df_cst)} registros)")
            st.info(f"🧮 Calculadora inicializada e pronta para uso!")
            
            with st.expander("👀 Preview dos dados CST"):
                st.dataframe(df_cst.head(10))
            
            return True
            
        except Exception as e:
            st.error(f"Erro ao carregar tabela CST: {str(e)}")
            return False
    
    def process_xml_files(self, uploaded_files: List) -> bool:
        """Processa arquivos XML das notas fiscais"""
        self.notas_processadas = []
        self.comparativos = []
        
        # Container para status e progresso
        status_container = st.container()
        
        with status_container:
            st.markdown("### 🔄 Processando Arquivos...")
            progress_bar = st.progress(0)
            status_text = st.empty()
            debug_expander = st.expander("🔍 Log de Processamento", expanded=True)
        
        total_files = len(uploaded_files)
        processed_count = 0
        
        for i, uploaded_file in enumerate(uploaded_files):
            try:
                # Atualiza status
                current_status = f"📄 Processando arquivo {i+1}/{total_files}: {uploaded_file.name}"
                status_text.text(current_status)
                
                with debug_expander:
                    st.write(f"▶️ Iniciando processamento de **{uploaded_file.name}**")
                
                # Lê conteúdo do arquivo
                xml_content = uploaded_file.read().decode('utf-8')
                
                with debug_expander:
                    st.write(f"   ✅ Arquivo lido: {len(xml_content)} caracteres")
                
                # Valida XML
                with debug_expander:
                    st.write(f"   🔍 Validando estrutura NFe...")
                
                is_valid, error_msg = validate_xml_nfe(xml_content)
                if not is_valid:
                    with debug_expander:
                        st.write(f"   ❌ **Validação falhou**: {error_msg}")
                    st.warning(f"⚠️ Arquivo {uploaded_file.name}: {error_msg}")
                    progress_bar.progress((i + 1) / total_files)
                    continue
                
                with debug_expander:
                    st.write(f"   ✅ Validação passou")
                    st.write(f"   🔄 Fazendo parse da nota fiscal...")
                
                # Faz parse da nota fiscal
                nota_fiscal = self.parser.parse_nota_fiscal(xml_content)
                
                with debug_expander:
                    st.write(f"   ✅ Parse concluído: {len(nota_fiscal.itens)} itens encontrados")
                    st.write(f"   💰 Valor total: R$ {nota_fiscal.valor_total_produtos:.2f}")
                
                self.notas_processadas.append(nota_fiscal)
                processed_count += 1
                
                # Calcula comparativo se calculadora estiver disponível
                if self.calculator:
                    with debug_expander:
                        st.write(f"   🧮 Calculando comparativo tributário...")
                    
                    comparativo = self.calculator.calcular_comparativo(nota_fiscal)
                    self.comparativos.append(comparativo)
                    
                    with debug_expander:
                        st.write(f"   ✅ Comparativo calculado")
                        st.write(f"   📊 Tributos atuais: R$ {sum(comparativo.tributacao_atual.values()):.2f}")
                        st.write(f"   🔄 Tributos reforma: R$ {sum(comparativo.tributacao_nova.values()):.2f}")
                else:
                    with debug_expander:
                        st.write(f"   ❌ **ERRO: Calculadora não disponível!**")
                        st.write(f"   💡 Verifique se a tabela CST foi carregada corretamente")
                        st.write(f"   🔍 Status calculadora: {self.calculator}")
                        st.write(f"   🔍 Status CST: {st.session_state.get('cst_loaded', False)}")
                
                progress_bar.progress((i + 1) / total_files)
                
                with debug_expander:
                    st.write(f"   🎉 **{uploaded_file.name}** processado com sucesso!")
                    st.markdown("---")
                
            except NFParserError as e:
                error_msg = f"❌ Erro de parser ao processar {uploaded_file.name}: {str(e)}"
                with debug_expander:
                    st.write(f"   ❌ **Erro de Parser**: {str(e)}")
                st.error(error_msg)
                progress_bar.progress((i + 1) / total_files)
                continue
            except Exception as e:
                error_msg = f"❌ Erro inesperado ao processar {uploaded_file.name}: {str(e)}"
                with debug_expander:
                    st.write(f"   ❌ **Erro Inesperado**: {str(e)}")
                    # Adiciona traceback para debug
                    import traceback
                    st.code(traceback.format_exc())
                st.error(error_msg)
                progress_bar.progress((i + 1) / total_files)
                continue
        
        # Finaliza processamento
        status_text.text("✅ Processamento concluído!")
        progress_bar.progress(1.0)
        
        # Resultado final
        if self.notas_processadas:
            success_msg = f"🎉 {processed_count} de {total_files} nota(s) fiscal(is) processada(s) com sucesso!"
            st.success(success_msg)
            
            with debug_expander:
                st.write(f"**RESUMO FINAL:**")
                st.write(f"- Total de arquivos: {total_files}")
                st.write(f"- Processados com sucesso: {processed_count}")
                st.write(f"- Valor total processado: R$ {sum(n.valor_total_produtos for n in self.notas_processadas):.2f}")
            
            # Limpa a interface após sucesso
            import time
            time.sleep(2)
            progress_bar.empty()
            status_text.empty()
            
            return True
        else:
            st.error("❌ Nenhuma nota fiscal foi processada com sucesso")
            
            with debug_expander:
                st.write("**RESULTADO**: Nenhum arquivo foi processado com sucesso")
                st.write("**SUGESTÕES**:")
                st.write("- Verifique se os arquivos são XMLs de NFe válidos")
                st.write("- Verifique se a tabela de CST foi carregada")
                st.write("- Consulte os logs acima para detalhes dos erros")
            
            return False
    
    def render_summary_metrics(self):
        """Renderiza métricas resumidas"""
        if not self.comparativos:
            return
        
        # Calcula totais consolidados
        total_produtos = sum(c.nota_fiscal.valor_total_produtos for c in self.comparativos)
        total_atual = sum(c.tributacao_atual['TOTAL'] for c in self.comparativos)
        total_rti = sum(c.tributacao_nova['TOTAL'] for c in self.comparativos)
        economia_total = total_rti - total_atual
        economia_percentual = (economia_total / total_atual * 100) if total_atual > 0 else 0
        
        st.markdown("### 📊 Resumo Consolidado")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "💰 Valor Total Produtos",
                format_currency(total_produtos),
                help="Soma do valor de todos os produtos das notas fiscais"
            )
        
        with col2:
            st.metric(
                "🏛️ Tributação Atual",
                format_currency(total_atual),
                help="Total de PIS + COFINS + IPI + ICMS"
            )
        
        with col3:
            st.metric(
                "🆕 Tributação RTI",
                format_currency(total_rti),
                help="Total de CBS + IBS conforme nova legislação"
            )
        
        with col4:
            delta_color = "normal" if economia_total >= 0 else "inverse"
            st.metric(
                "📈 Diferença",
                format_currency(abs(economia_total)),
                delta=f"{economia_percentual:.2f}%",
                delta_color=delta_color,
                help="Diferença entre tributação RTI e atual (negativo = economia)"
            )
        
        # Mensagem de economia
        st.markdown("---")
        economy_msg = get_economy_message(Decimal(str(economia_total)), Decimal(str(economia_percentual)))
        
        if economia_total < 0:
            st.markdown(f'<div class="economy-positive">{economy_msg}</div>', unsafe_allow_html=True)
        elif economia_total > 0:
            st.markdown(f'<div class="economy-negative">{economy_msg}</div>', unsafe_allow_html=True)
        else:
            st.info(economy_msg)
    
    def render_detailed_comparison(self):
        """Renderiza comparação detalhada por tributo"""
        if not self.comparativos:
            return
        
        st.markdown("### 🔍 Comparação Detalhada por Tributo")
        
        # Consolida tributos
        tributos_atuais = {
            'PIS': sum(c.tributacao_atual.get('PIS', Decimal('0')) for c in self.comparativos),
            'COFINS': sum(c.tributacao_atual.get('COFINS', Decimal('0')) for c in self.comparativos),
            'IPI': sum(c.tributacao_atual.get('IPI', Decimal('0')) for c in self.comparativos),
            'ICMS': sum(c.tributacao_atual.get('ICMS', Decimal('0')) for c in self.comparativos)
        }
        
        tributos_rti = {
            'CBS': sum(c.tributacao_nova.get('CBS', Decimal('0')) for c in self.comparativos),
            'IBS': sum(c.tributacao_nova.get('IBS', Decimal('0')) for c in self.comparativos)
        }
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🏛️ Tributação Atual")
            for tributo, valor in tributos_atuais.items():
                if valor > 0:
                    st.markdown(f"**{tributo}**: {format_currency(valor)}")
        
        with col2:
            st.subheader("🆕 Tributação RTI")
            for tributo, valor in tributos_rti.items():
                if valor > 0:
                    st.markdown(f"**{tributo}**: {format_currency(valor)}")
        
        # Gráfico de comparação
        self.render_comparison_chart(tributos_atuais, tributos_rti)
    
    def render_comparison_chart(self, tributos_atuais: Dict, tributos_rti: Dict):
        """Renderiza gráfico de comparação de tributos"""
        
        # Prepara dados para o gráfico
        labels_atual = [k for k, v in tributos_atuais.items() if v > 0]
        values_atual = [float(v) for k, v in tributos_atuais.items() if v > 0]
        
        labels_rti = [k for k, v in tributos_rti.items() if v > 0]
        values_rti = [float(v) for k, v in tributos_rti.items() if v > 0]
        
        if not values_atual and not values_rti:
            return
        
        # Cria subplots
        fig = make_subplots(
            rows=1, cols=2,
            specs=[[{"type": "pie"}, {"type": "pie"}]],
            subplot_titles=("Tributação Atual", "Tributação RTI")
        )
        
        # Gráfico tributação atual
        if values_atual:
            fig.add_trace(
                go.Pie(
                    labels=labels_atual,
                    values=values_atual,
                    name="Atual",
                    marker_colors=['#e74c3c', '#3498db', '#f39c12', '#9b59b6']
                ),
                row=1, col=1
            )
        
        # Gráfico tributação RTI
        if values_rti:
            fig.add_trace(
                go.Pie(
                    labels=labels_rti,
                    values=values_rti,
                    name="RTI",
                    marker_colors=['#27ae60', '#2ecc71']
                ),
                row=1, col=2
            )
        
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(
            title_text="Comparação de Tributos: Atual vs RTI",
            title_x=0.5,
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def render_detailed_table(self):
        """Renderiza tabela detalhada por item"""
        if not self.comparativos:
            return
        
        st.markdown("### 📋 Detalhamento por Item")
        
        # Consolida todos os detalhes
        all_details = []
        for i, comparativo in enumerate(self.comparativos):
            for detail in comparativo.detalhes_por_item:
                detail_copy = detail.copy()
                detail_copy['nota'] = f"NF {comparativo.nota_fiscal.numero}"
                all_details.append(detail_copy)
        
        if not all_details:
            st.warning("Nenhum detalhe disponível para exibição")
            return
        
        # Cria DataFrame
        df_details = pd.DataFrame(all_details)
        
        # Formata colunas monetárias
        money_cols = ['valor_produto', 'pis_atual', 'cofins_atual', 'ipi_atual', 'icms_atual', 
                     'total_atual', 'cbs_novo', 'ibs_novo', 'total_rti', 'diferenca']
        
        for col in money_cols:
            if col in df_details.columns:
                df_details[f'{col}_formatted'] = df_details[col].apply(lambda x: format_currency(x))
        
        # Seleciona e renomeia colunas para exibição
        display_cols = {
            'nota': 'Nota Fiscal',
            'item': 'Item',
            'descricao': 'Descrição',
            'ncm': 'NCM',
            'valor_produto_formatted': 'Valor Produto',
            'total_atual_formatted': 'Tributos Atuais',
            'total_rti_formatted': 'Tributos RTI',
            'diferenca_formatted': 'Diferença',
            'economia_percentual': 'Economia %'
        }
        
        df_display = df_details[[col for col in display_cols.keys() if col in df_details.columns]].copy()
        df_display = df_display.rename(columns=display_cols)
        
        # Formata porcentagem
        if 'Economia %' in df_display.columns:
            df_display['Economia %'] = df_display['Economia %'].apply(lambda x: f"{x:.2f}%")
        
        # Exibe tabela
        st.dataframe(
            df_display,
            use_container_width=True,
            height=400
        )
        
        # Estatísticas da tabela
        stats = generate_summary_stats(all_details)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📦 Total de Itens", stats['total_itens'])
        with col2:
            st.metric("📉 Itens com Economia", stats['itens_com_economia'])
        with col3:
            st.metric("📈 Itens com Aumento", stats['itens_com_aumento'])
        with col4:
            st.metric("➡️ Sem Alteração", stats['itens_sem_alteracao'])
    
    def render_download_section(self):
        """Renderiza seção de download de relatórios"""
        if not self.comparativos:
            return
        
        st.markdown("### 💾 Download de Relatórios")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # CSV detalhado
            if st.button("📄 Gerar Relatório CSV"):
                csv_data = self.generate_csv_report()
                st.download_button(
                    label="⬇️ Download CSV",
                    data=csv_data,
                    file_name="relatorio_tributario_rti.csv",
                    mime="text/csv"
                )
        
        with col2:
            # Resumo executivo
            if st.button("📊 Gerar Resumo Executivo"):
                summary_data = self.generate_executive_summary()
                st.download_button(
                    label="⬇️ Download Resumo",
                    data=summary_data,
                    file_name="resumo_executivo_rti.txt",
                    mime="text/plain"
                )
    
    def generate_csv_report(self) -> str:
        """Gera relatório CSV detalhado"""
        all_details = []
        for comparativo in self.comparativos:
            for detail in comparativo.detalhes_por_item:
                detail_copy = detail.copy()
                detail_copy['nota_numero'] = comparativo.nota_fiscal.numero
                detail_copy['nota_serie'] = comparativo.nota_fiscal.serie
                detail_copy['nota_data'] = comparativo.nota_fiscal.data_emissao
                detail_copy['emitente'] = comparativo.nota_fiscal.razao_social_emitente
                all_details.append(detail_copy)
        
        df = pd.DataFrame(all_details)
        return df.to_csv(index=False, sep=';', encoding='utf-8-sig')
    
    def generate_executive_summary(self) -> str:
        """Gera resumo executivo em texto"""
        if not self.comparativos:
            return "Nenhum dado disponível para gerar resumo."
        
        # Calcula totais
        total_produtos = sum(c.nota_fiscal.valor_total_produtos for c in self.comparativos)
        total_atual = sum(c.tributacao_atual['TOTAL'] for c in self.comparativos)
        total_rti = sum(c.tributacao_nova['TOTAL'] for c in self.comparativos)
        economia_total = total_rti - total_atual
        economia_percentual = (economia_total / total_atual * 100) if total_atual > 0 else 0
        
        summary = f"""
RELATÓRIO EXECUTIVO - ANÁLISE TRIBUTÁRIA RTI
============================================

DADOS GERAIS:
- Período de Análise: {self.comparativos[0].nota_fiscal.data_emissao if self.comparativos else 'N/A'}
- Número de Notas Fiscais: {len(self.comparativos)}
- Valor Total dos Produtos: {format_currency(total_produtos)}

TRIBUTAÇÃO ATUAL:
- Total de Tributos: {format_currency(total_atual)}
- Carga Tributária: {(total_atual / total_produtos * 100):.2f}%

TRIBUTAÇÃO RTI (PROJETADA):
- Total de Tributos: {format_currency(total_rti)}
- Carga Tributária: {(total_rti / total_produtos * 100):.2f}%

RESULTADO DA ANÁLISE:
- Diferença Total: {format_currency(abs(economia_total))}
- Variação Percentual: {economia_percentual:.2f}%
- Resultado: {'ECONOMIA' if economia_total < 0 else 'AUMENTO' if economia_total > 0 else 'SEM ALTERAÇÃO'}

OBSERVAÇÕES:
- Esta análise é baseada na proposta atual da PLP 39/2015
- Os valores podem variar conforme alterações na legislação
- Recomenda-se acompanhar as atualizações da reforma tributária

Gerado em: {pd.Timestamp.now().strftime('%d/%m/%Y às %H:%M')}
"""
        return summary
    
    def render_sidebar_config(self):
        """Renderiza configurações na sidebar"""
        st.sidebar.markdown("### ⚙️ Configurações RTI")
        
        # Status da calculadora - DEBUG
        st.sidebar.markdown("### 🔍 Status do Sistema")
        
        # Status da calculadora
        if self.calculator:
            st.sidebar.success("✅ Calculadora: Ativa")
            if hasattr(self.calculator, 'cst_data') and self.calculator.cst_data is not None:
                st.sidebar.info(f"📋 CST: {len(self.calculator.cst_data)} registros")
        else:
            st.sidebar.error("❌ Calculadora: Não inicializada")
        
        # Status da sessão
        st.sidebar.write(f"CST Sessão: {'✅' if st.session_state.cst_loaded else '❌'}")
        if st.session_state.df_cst is not None:
            st.sidebar.write(f"Dados CST: ✅ {len(st.session_state.df_cst)} registros")
        else:
            st.sidebar.write("Dados CST: ❌ Não carregados")
            
        st.sidebar.markdown("---")
        
        # Configurações de alíquotas
        cbs_rate = st.sidebar.slider(
            "CBS (%)",
            min_value=0.0,
            max_value=5.0,
            value=0.9,
            step=0.1,
            help="Alíquota da Contribuição sobre Bens e Serviços"
        )
        
        ibs_rate = st.sidebar.slider(
            "IBS (%)",
            min_value=0.0,
            max_value=30.0,
            value=26.0,
            step=0.5,
            help="Alíquota do Imposto sobre Bens e Serviços"
        )
        
        # Atualiza configuração se mudou
        if self.calculator:
            self.calculator.config_rti.cbs_aliquota = Decimal(str(cbs_rate / 100))
            self.calculator.config_rti.ibs_aliquota = Decimal(str(ibs_rate / 100))
        
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 📚 Recursos")
        
        if st.sidebar.button("🔄 Reprocessar Cálculos"):
            if self.notas_processadas and self.calculator:
                self.comparativos = []
                for nota in self.notas_processadas:
                    comparativo = self.calculator.calcular_comparativo(nota)
                    self.comparativos.append(comparativo)
                st.rerun()
        
        st.sidebar.markdown("### ℹ️ Sobre a Aplicação")
        st.sidebar.info("""
        📊 **Análise Tributária RTI**
        
        Compare a tributação atual com a Reforma Tributária (PLP 39/2015).
        
        📖 Acesse o **Manual de Uso** para instruções detalhadas.
        """)
    
    def run(self):
        """Executa a aplicação principal"""
        self.render_header()
        self.render_plp_info()
        self.render_sidebar_config()
        
        # Upload de arquivos
        st.markdown("## 📤 Upload de Arquivos")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 Tabela de CST")
            cst_file = st.file_uploader(
                "Carregue a planilha de CST e Classificação Tributária",
                type=['xlsx', 'xls'],
                help="Arquivo Excel com as configurações de CST para a RTI"
            )
            
            if cst_file and not st.session_state.cst_loaded:
                if self.load_cst_table(cst_file):
                    st.session_state.cst_loaded = True
        
        with col2:
            st.markdown("### 📄 Notas Fiscais (XML)")
            xml_files = st.file_uploader(
                "Carregue os arquivos XML das Notas Fiscais",
                type=['xml'],
                accept_multiple_files=True,
                help="Aceita múltiplos arquivos XML de NF-e ou NFC-e"
            )
        
        # Processamento
        if xml_files and st.session_state.cst_loaded:
            if st.button("🚀 Processar Análise Tributária", type="primary"):
                # Verifica se calculadora ainda está disponível
                if not self.calculator:
                    st.warning("⚠️ Calculadora não encontrada. Tentando reinicializar...")
                    # Tenta recarregar a calculadora
                    if hasattr(st.session_state, 'df_cst') and st.session_state.df_cst is not None:
                        config = ConfigTributacao()
                        self.calculator = CalculadoraTributaria(config)
                        self.calculator.carregar_tabela_cst(st.session_state.df_cst)
                        st.success("✅ Calculadora reinicializada!")
                    else:
                        st.error("❌ Não foi possível reinicializar a calculadora. Recarregue a tabela CST.")
                        st.stop()
                
                if self.process_xml_files(xml_files):
                    st.session_state.processed_files = xml_files
        
        # Resultados
        if self.comparativos:
            st.markdown("---")
            st.markdown("## 📈 Resultados da Análise")
            
            self.render_summary_metrics()
            st.markdown("---")
            self.render_detailed_comparison()
            st.markdown("---")
            self.render_detailed_table()
            st.markdown("---")
            self.render_download_section()
        
        elif xml_files and not st.session_state.cst_loaded:
            st.warning("⚠️ Carregue primeiro a tabela de CST para processar as notas fiscais")
        
        elif not xml_files:
            st.info("💡 Carregue os arquivos XML das notas fiscais para iniciar a análise")


# Ponto de entrada da aplicação
if __name__ == "__main__":
    app = TributaryApp()
    app.run()
