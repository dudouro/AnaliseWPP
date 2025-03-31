import streamlit as st
import pandas as pd
import plotly.express as px
from wordcloud import WordCloud
from io import BytesIO
from auxiliar import process_whatsapp_chat, classificar_mensagens

st.title("Análise de Grupo do WhatsApp")

# Etapa 1: Criar a interface básica e permitir upload de arquivo
# Prompt para o ChatGPT:
# "Crie uma interface Streamlit que permita o upload de um arquivo .txt"
uploaded_file = st.file_uploader("Carregue o arquivo de conversa (.txt)", type=["txt"])


if uploaded_file is not None:
    # Etapa 2: Processar os dados do arquivo e exibir uma prévia
    # Prompt para o ChatGPT:
    # "Crie uma função que processe um arquivo de conversa do WhatsApp e exiba uma prévia dos dados em um DataFrame no Streamlit"
    df = process_whatsapp_chat(uploaded_file)
    df = classificar_mensagens(df)
    st.write("Prévia dos dados processados:")
    st.dataframe(df.head(15))
    
    # Substitua a parte do download por esta versão simplificada
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:  # Usando openpyxl em vez de xlsxwriter
        df.to_excel(writer, index=False, sheet_name='Dados_WhatsApp')
        
    st.download_button(
        label="Download dos dados processados (XLSX)",
        data=output.getvalue(),
        file_name='dados_processados.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    
    # Etapa 3: Criar gráfico de linha com contagem de mensagens por dia
    # Prompt para o ChatGPT:
    # "Crie um gráfico de linha no Streamlit que mostre a quantidade de mensagens enviadas por dia, usando Plotly"
    st.subheader("Atividade diária no grupo")
    df["Dia"] = pd.to_datetime(df["Dia"], errors='coerce')  # Correção da conversão de data
    daily_counts = df.groupby("Dia").size().reset_index(name="Contagem de Mensagens")
    fig_daily = px.line(daily_counts, x="Dia", y="Contagem de Mensagens", title="Mensagens enviadas por dia")
    st.plotly_chart(fig_daily, use_container_width=True)
    
    # Etapa 4: Criar gráfico de frequência de mensagens por horário
    # Prompt para o ChatGPT:
    # "Crie um histograma no Streamlit que mostre a distribuição de mensagens enviadas por horário, usando Plotly"
    st.subheader("Distribuição de Mensagens por Hora")
    fig_hourly = px.histogram(df, x='Horário', nbins=24, title="Distribuição de Mensagens por Hora", labels={'Horário': 'Hora do Dia'}, opacity=0.7)
    st.plotly_chart(fig_hourly, use_container_width=True)
    
    # Etapa 5: Criar gráfico de distribuição de mensagens por dia da semana
    # Prompt para o ChatGPT:
    # "Crie um gráfico de barras no Streamlit que mostre a quantidade de mensagens enviadas por dia da semana, usando Plotly"
    st.subheader("Distribuição de Mensagens por Dia da Semana")
    df["Dia da Semana"] = df["Dia"].dt.day_name()
    order = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    weekday_counts = df["Dia da Semana"].value_counts().reindex(order).reset_index()
    weekday_counts.columns = ["Dia da Semana", "Contagem de Mensagens"]
    fig_weekday = px.bar(weekday_counts, x="Dia da Semana", y="Contagem de Mensagens", title="Mensagens enviadas por dia da semana")
    st.plotly_chart(fig_weekday, use_container_width=True)
    
    # Etapa 6: Criar um mapa de palavras mais usadas
    # Prompt para o ChatGPT:
    # "Crie uma nuvem de palavras no Streamlit que exiba as palavras mais usadas nas mensagens do grupo WhatsApp"
    st.subheader("Palavras mais usadas no grupo")
    text = " ".join(df["Mensagem"].dropna())
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
    
    img = BytesIO()
    wordcloud.to_image().save(img, format='PNG')
    st.image(img, caption="Nuvem de palavras", use_column_width=True)
    
    
    #Etapa Extra: 
    # Contagem de mensagens por Semestre e Período do Semestre
    # Prompt para o ChatGPT: 
    # "Crie um gráfico de barras no Streamlit que mostre a quantidade de mensagens enviadas por semestre e período do semestre, usando Plotly"
    # Definir a ordem correta dos períodos
    ordem_periodos = ["25%", "50%", "75%", "100%", "Férias"]

    # Converter a coluna "Periodo_Semestre" em uma categoria ordenada
    df["Periodo_Semestre"] = pd.Categorical(df["Periodo_Semestre"], categories=ordem_periodos, ordered=True)

    # Contar quantas mensagens foram enviadas por semestre e período
    contagem_mensagens = df.groupby(["Semestre", "Periodo_Semestre"]).size().reset_index(name="Quantidade")

    # Criar o gráfico corrigido
    fig = px.bar(
        contagem_mensagens,
        x="Semestre",
        y="Quantidade",
        color="Periodo_Semestre",
        barmode="group",
        category_orders={"Periodo_Semestre": ordem_periodos},  # Ordenação correta
        labels={"Quantidade": "Número de Mensagens", "Periodo_Semestre": "Período"},
        title="Distribuição de Mensagens por Semestre e Período",
        color_discrete_map={"25%": "blue", "50%": "red", "75%": "pink", "100%": "lightblue", "Férias": "green"}
    )

    # Exibir no Streamlit
    st.plotly_chart(fig)
