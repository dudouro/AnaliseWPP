import streamlit as st
import pandas as pd
import plotly.express as px
from wordcloud import WordCloud
from io import BytesIO
from auxiliar import process_whatsapp_chat

st.title("Análise Individual de Participante do WhatsApp")

# Configuração inicial
st.sidebar.header("Filtros")
uploaded_file = st.sidebar.file_uploader("Carregue o arquivo de conversa (.txt)", type=["txt"])

if uploaded_file is not None:
    # Processar os dados
    df = process_whatsapp_chat(uploaded_file)
    
    # Verificar se a coluna Telefone existe
    if 'Telefone' not in df.columns:
        st.error("A coluna 'Telefone' não foi encontrada nos dados processados.")
        st.write("Colunas disponíveis:", df.columns.tolist())
        st.stop()
    
    # Sidebar - Seleção de participante
    participantes = df['Telefone'].unique()
    participante_selecionado = st.sidebar.selectbox(
        "Selecione o participante para análise:",
        options=participantes,
        index=0
    )
    
    # Filtrar dados para o participante selecionado
    df_participante = df[df['Telefone'] == participante_selecionado]
    
    st.header(f"Análise do participante: {participante_selecionado}")
    
    # Métricas principais
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total de Mensagens", len(df_participante))
    with col2:
        st.metric("Dias ativos", df_participante['Dia'].nunique())
    with col3:
        st.metric("Primeira participação", df_participante['Dia'].min().strftime('%d/%m/%Y'))
    
    # Gráfico 1: Atividade ao longo do tempo
    st.subheader(f"Atividade por dia")
    df_participante["Dia"] = pd.to_datetime(df_participante["Dia"])
    daily_counts = df_participante.groupby("Dia").size().reset_index(name="Mensagens")
    fig_daily = px.line(daily_counts, x="Dia", y="Mensagens")
    st.plotly_chart(fig_daily, use_container_width=True)
    
    # Gráfico 2: Horário preferido
    st.subheader(f"Distribuição por horário")
    fig_hourly = px.histogram(df_participante, x='Horário', nbins=24, 
                             color_discrete_sequence=['#FFA07A'])
    st.plotly_chart(fig_hourly, use_container_width=True)
    
    # Gráfico 3: Dia da semana preferido
    st.subheader(f"Atividade por dia da semana")
    df_participante["Dia da Semana"] = df_participante["Dia"].dt.day_name()
    weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    weekday_counts = df_participante["Dia da Semana"].value_counts().reindex(weekday_order).reset_index()
    weekday_counts.columns = ["Dia da Semana", "Mensagens"]
    
    fig_weekday = px.bar(weekday_counts, x="Dia da Semana", y="Mensagens",
                        color="Dia da Semana")
    st.plotly_chart(fig_weekday, use_container_width=True)
    
    # Nuvem de palavras pessoal
    st.subheader(f"Palavras mais usadas")
    text = " ".join(df_participante["Mensagem"].dropna())
    if text:
        wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
        img = BytesIO()
        wordcloud.to_image().save(img, format='PNG')
        st.image(img, use_column_width=True)
    else:
        st.warning("Não há mensagens textuais disponíveis para gerar nuvem de palavras.")
    
    # Download dos dados do participante
    st.subheader("Exportar dados")
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_participante.to_excel(writer, index=False, sheet_name='Dados_Participante')
        
    st.download_button(
        label=f"Baixar dados do participante (XLSX)",
        data=output.getvalue(),
        file_name=f'dados_whatsapp_{participante_selecionado}.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    
    # Visualização das mensagens
    st.subheader(f"Últimas mensagens")
    st.dataframe(df_participante[['Dia', 'Horário', 'Mensagem']].sort_values('Dia', ascending=False).head(20))
else:
    st.info("Por favor, carregue um arquivo de conversa do WhatsApp para começar a análise.")