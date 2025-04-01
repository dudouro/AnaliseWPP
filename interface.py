import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
from io import BytesIO
import numpy as np

from auxiliar import process_whatsapp_chat, stopwords_pt, analyze_sentiments

# Configuração da página
st.set_page_config(page_title="WhatsApp Analyzer", layout="wide")

# Título principal
st.title("📱 Análise Individual de Participante do WhatsApp")

# ==================================================
# FUNÇÕES AUXILIARES
# ==================================================

def show_export_tutorial():
    """Exibe o tutorial de exportação de conversas na sidebar"""
    with st.sidebar.expander("📌 Como exportar conversas do WhatsApp"):
        st.markdown("""
        **Siga esses passos para exportar suas conversas:**  
        (As imagens são ilustrativas - caminhos podem variar por dispositivo)
        """)
        
        steps = [
            ("**Passo 1:** Toque nos três pontos (⋮) e selecione **Configurações**", "passo1.jpeg"),
            ("**Passo 2:** Selecione **Conversas**", "passo2.jpeg"),
            ("**Passo 3:** Selecione **Histórico de Conversas**", "passo3.jpeg"),
            ("**Passo 4:** Selecione **Exportar Conversa**", "passo4.jpeg"),
            ("**Passo 5:** Selecione a conversa para análise", "passo5.jpeg"),
            ("**Passo 6:** Escolha incluir mídia ou não", "passo6.jpeg"),
            ("**Passo 7:** Extraia o arquivo de texto (.txt)", "passo7.jpeg"),
        ]

        for description, image in steps:
            with st.container():
                st.markdown(description)
                try:
                    st.image(f"imagens/{image}", width=250)
                except FileNotFoundError:
                    st.warning(f"Imagem {image} não encontrada")

def create_main_metrics(df: pd.DataFrame):
    """Cria as métricas principais na interface"""
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total de Mensagens", len(df))
    with col2:
        st.metric("Dias ativos", df['Dia'].nunique())
    with col3:
        st.metric("Primeira participação", df['Dia'].min().strftime('%d/%m/%Y'))

def plot_sentiment_evolution(df: pd.DataFrame):
    """Gera o gráfico de evolução temporal de sentimentos"""
    # Converter a coluna 'Dia' para datetime
    df['Dia'] = pd.to_datetime(df['Dia'], errors='coerce')  # Adicionado conversão segura
    
    # Remover linhas com datas inválidas (caso existam)
    df = df.dropna(subset=['Dia'])
    
    # Criar coluna de mês
    df['Mês'] = df['Dia'].dt.to_period('M').dt.to_timestamp()  # Corrigido nome da coluna
    
    # Restante do código permanece igual...
    monthly_sentiment = df.groupby(['Mês', 'sentimento']).size().unstack(fill_value=0)
    
    monthly_data = pd.DataFrame({
        'Mês': monthly_sentiment.index,
        'Positivo': monthly_sentiment.get('positivo', 0),
        'Negativo': -monthly_sentiment.get('negativo', 0)
    })

    # ... (restante do código da função)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=monthly_data['Mês'],
        y=monthly_data['Positivo'],
        mode='lines+markers',
        name='Positivo',
        line=dict(color='#4CAF50', width=3),
        marker=dict(size=8))
    )
    fig.add_trace(go.Scatter(
        x=monthly_data['Mês'],
        y=monthly_data['Negativo'],
        mode='lines+markers',
        name='Negativo',
        line=dict(color='#F44336', width=3),
        marker=dict(size=8))
    )
    fig.add_hline(
        y=0,
        line=dict(color='#607D8B', width=2, dash='dot'),
        annotation_text="Linha Neutra",
        annotation_position="bottom right"
    )
    fig.update_layout(
        title='Evolução Mensal de Sentimentos',
        yaxis=dict(
            title='Intensidade de Sentimentos',
            tickvals=np.arange(-monthly_data['Negativo'].min(), monthly_data['Positivo'].max()+1, 5),
            ticktext=[str(abs(x)) for x in np.arange(-monthly_data['Negativo'].min(), monthly_data['Positivo'].max()+1, 5)],
            showgrid=True
        ),
        xaxis=dict(title='Mês', tickformat='%b %Y'),
        hovermode='x unified',
        plot_bgcolor='rgba(0,0,0,0)',
        height=500
    )
    return fig

# ==================================================
# BARRA LATERAL
# ==================================================

st.sidebar.header("Configurações")
uploaded_file = st.sidebar.file_uploader(
    "Carregue o arquivo de conversa (.txt)",
    type=["txt"],
    help="Arquivo exportado do WhatsApp via 'Exportar conversa sem mídia'"
)

show_export_tutorial()

# ==================================================
# CORPO PRINCIPAL
# ==================================================

if uploaded_file is not None:
    # Processamento inicial dos dados
    df = process_whatsapp_chat(uploaded_file)
    
    if 'Telefone' not in df.columns:
        st.error("Erro na estrutura dos dados: coluna 'Telefone' não encontrada")
        st.stop()

    # Seleção de participante
    participante_selecionado = st.sidebar.selectbox(
        "Selecione o participante:",
        options=df['Telefone'].unique(),
        index=0
    )
    
    df_participante = df[df['Telefone'] == participante_selecionado]
    
    # Seção principal
    st.header(f"🔍 Análise de {participante_selecionado}")
    create_main_metrics(df_participante)
    
    # Análise de sentimentos
    st.subheader("📊 Análise de Sentimentos")
    df_with_sentiment, sentiment_stats = analyze_sentiments(df_participante)
    
    cols = st.columns(3)
    cols[0].metric("Positivas", f"{sentiment_stats['percent_positivo']:.1f}%")
    cols[1].metric("Negativas", f"{sentiment_stats['percent_negativo']:.1f}%")
    cols[2].metric("Neutras", f"{sentiment_stats['percent_neutro']:.1f}%")
    
    # Gráficos de sentimentos
    col1, col2 = st.columns([3, 2])
    with col1:
        st.plotly_chart(plot_sentiment_evolution(df_with_sentiment), use_container_width=True)
    with col2:
        fig_pie = px.pie(
            names=list(sentiment_stats['contagem_sentimentos'].keys()),
            values=list(sentiment_stats['contagem_sentimentos'].values()),
            title='Distribuição de Sentimentos'
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    # Visualização temporal
    st.subheader("⏰ Padrões Temporais")
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico 2: Horário preferido
        st.subheader(f"Distribuição por horário")
        fig_hourly = px.histogram(df_participante, x='Horário', nbins=24, 
                                color_discrete_sequence=['#FFA07A'])
        st.plotly_chart(fig_hourly, use_container_width=True)
    
    with col2:
        # Gráfico de atividade por dia da semana (versão corrigida e melhorada)
        st.subheader("Distribuição por dia")

        try:
            # Converter para datetime se necessário
            if not pd.api.types.is_datetime64_any_dtype(df_participante["Dia"]):
                df_participante["Dia"] = pd.to_datetime(df_participante["Dia"], errors='coerce')
            
            # Extrair nome do dia em português
            dias_portugues = {
                'Monday': 'Segunda',
                'Tuesday': 'Terça',
                'Wednesday': 'Quarta',
                'Thursday': 'Quinta',
                'Friday': 'Sexta',
                'Saturday': 'Sábado',
                'Sunday': 'Domingo'
            }
            
            # Criar coluna com dias em português
            df_participante["Dia da Semana"] = df_participante["Dia"].dt.day_name().map(dias_portugues)
            
            # Ordem correta em português
            ordem_dias = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
            
            # Contagem e ordenação
            contagem_dias = (
                df_participante["Dia da Semana"]
                .value_counts()
                .reindex(ordem_dias, fill_value=0)
                .reset_index()
            )
            contagem_dias.columns = ["Dia da Semana", "Mensagens"]

            # Criar gráfico
            fig = px.bar(
                contagem_dias,
                x="Dia da Semana",
                y="Mensagens",
                color="Dia da Semana",
                color_discrete_sequence=px.colors.sequential.Viridis,
                labels={'Mensagens': 'Total de Mensagens', 'Dia da Semana': ''},
            )
            
            # Ajustes finais
            fig.update_layout(
                xaxis={'categoryorder': 'array', 'categoryarray': ordem_dias},
                showlegend=False,
                hovermode="x unified"
            )
            
            st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error(f"Erro ao gerar gráfico de dias: {str(e)}")
            st.write("Dados usados:", df_participante[["Dia"]].head())

    # Nuvem de palavras
    st.subheader("💬 Palavras Mais Frequentes")
    text = " ".join(df_participante["Mensagem"].dropna())
    
    if text:
        wordcloud = WordCloud(
            width=800, 
            height=400, 
            background_color='white',
            stopwords=stopwords_pt
        ).generate(text)
        
        st.image(wordcloud.to_image(), use_container_width=True)
    else:
        st.warning("Não há mensagens textuais para exibir")

    # Dados brutos
    st.subheader("📋 Últimas Mensagens")
    st.dataframe(
        df_participante[['Dia', 'Horário', 'Mensagem']]
        .sort_values('Dia', ascending=False)
        .head(20)
        .style.format({'Dia': lambda t: t.strftime("%d/%m/%Y %H:%M")}),
        height=400
    )

    # Exportação de dados
    st.subheader("📤 Exportar Dados")
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df_participante.to_excel(writer, index=False, sheet_name='Dados')
    
    st.download_button(
        label="Baixar dados completos (XLSX)",
        data=buffer.getvalue(),
        file_name=f'whatsapp_{participante_selecionado}.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

else:
    st.info("ℹ️ Por favor, carregue um arquivo de conversa do WhatsApp para iniciar a análise")
