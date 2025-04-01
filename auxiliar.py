import pandas as pd
import re

def process_whatsapp_chat(file):
    lines = file.getvalue().decode("utf-8").split("\n")

    # Padrão Android: "DD/MM/YYYY HH:MM - Nome: Mensagem"
    pattern_android = re.compile(r'^(\d{2}/\d{2}/\d{4}) (\d{2}:\d{2}) - ([^:]+?): (.*)')
    
    # Padrão iOS: "[DD/MM/YYYY, HH:MM:SS] Nome: Mensagem"
    pattern_ios = re.compile(r'^\[(\d{2}/\d{2}/\d{4}), (\d{2}:\d{2}:\d{2})\] ([^:]+?): (.*)')

    data = []
    current_entry = None
    is_ios = False  # Flag para detectar se é formato iOS

    for line in lines:
        line = line.strip()
        
        # Tenta casar o padrão do Android
        match_android = pattern_android.match(line)
        
        # Tenta casar o padrão do iOS
        match_ios = pattern_ios.match(line)

        if match_android:
            if current_entry:
                data.append(current_entry)

            dia, horario, telefone, mensagem = match_android.groups()
            current_entry = [dia, horario, telefone, mensagem]

        elif match_ios:
            is_ios = True  # Confirma que é iOS
            if current_entry:
                data.append(current_entry)

            dia, horario, telefone, mensagem = match_ios.groups()
            current_entry = [dia, horario, telefone, mensagem[:]]

        elif current_entry:
            current_entry[3] += '\n' + line  # Mensagem multilinha
        
    if current_entry:
        data.append(current_entry)

    df = pd.DataFrame(data, columns=['Dia', 'Horário', 'Telefone', 'Mensagem'])

    # Conversão de data e hora
    df['Dia'] = pd.to_datetime(df['Dia'], format='%d/%m/%Y').dt.date
    df['Horário'] = pd.to_datetime(df['Horário'], format='%H:%M:%S' if is_ios else '%H:%M').dt.hour
    
    # Filtra mensagens irrelevantes
    df = df[~df['Mensagem'].str.contains('<Mídia oculta>|Mensagem apagada|chat.whatsapp.com|https', na=False)]
    df = df[df['Mensagem'].str.strip() != ""]

    return df

stopwords_pt = {
    "a", "e", "não", "o", "que", "vc", "à", "é", "só", "tá", "vai", "acho", "n","nan","bit", "pq","pra", "q", "adeus", "agora", "ainda", "além", "algo", "algum", "alguma", "algumas", "alguns",
    "ali", "ampla", "amplas", "amplo", "amplos", "ano", "anos", "antes", "apenas", "apoio", "após",
    "aquela", "aquelas", "aquele", "aqueles", "aquilo", "área", "as", "assim", "até", "atrás", "através",
    "baixo", "bastante", "bem", "boa", "boas", "bom", "bons", "breve", "cada", "caminho", "catorze", 
    "cedo", "cento", "certamente", "certeza", "cima", "cinco", "coisa", "coisas", "com", "como", 
    "conselho", "contra", "contudo", "custa", "da", "dá", "dão", "daquela", "daquelas", "daquele",
    "daqueles", "dar", "das", "de", "debaixo", "demais", "dentro", "depois", "desde", "dessa", "dessas",
    "desse", "desses", "desta", "destas", "deste", "destes", "deve", "devem", "deverá", "dez", "dezanove",
    "dezasseis", "dezassete", "dezoito", "dia", "diante", "diz", "dizem", "dizer", "do", "dois", "dos",
    "doze", "duas", "dúvida", "e", "ela", "elas", "ele", "eles", "em", "embora", "enquanto", "entre",
    "era", "essa", "essas", "esse", "esses", "esta", "está", "estamos", "estão", "estar", "estas",
    "estás", "estava", "este", "esteja", "estejam", "estejamos", "estes", "esteve", "estive", "estivemos",
    "estiver", "estivera", "estiveram", "estiverem", "estivermos", "estivesse", "estivessem", "estiveste",
    "estivestes", "estivéramos", "estivéssemos", "estou", "eu", "exemplo", "falta", "fará", "favor",
    "faz", "fazeis", "fazem", "fazemos", "fazer", "fazes", "fez", "fim", "final", "foi", "fomos",
    "for", "fora", "foram", "forem", "forma", "formos", "fosse", "fossem", "foste", "fostes", "fui",
    "fôramos", "fôssemos", "geral", "grande", "grandes", "grupo", "hoje", "hora", "horas", "isso",
    "isto", "já", "lá", "lado", "lhe", "lhes", "logo", "longe", "lugar", "maior", "maioria", "mais",
    "mal", "mas", "máximo", "me", "meio", "menor", "menos", "mês", "meses", "meu", "meus", "mil",
    "minha", "minhas", "momento", "muito", "muitos", "na", "nada", "não", "naquela", "naquelas",
    "naquele", "naqueles", "nas", "nem", "nenhuma", "nessa", "nessas", "nesse", "nesses", "nesta",
    "nestas", "neste", "nestes", "ninguém", "nível", "no", "noite", "nome", "nos", "nós", "nossa",
    "nossas", "nosso", "nossos", "nova", "novas", "nove", "novo", "novos", "num", "numa", "número",
    "nunca", "o", "obra", "obrigada", "obrigado", "oitava", "oitavo", "oito", "onde", "ontem",
    "onze", "os", "ou", "outra", "outras", "outro", "outros", "para", "parece", "parte", "partir",
    "pegar", "pela", "pelas", "pelo", "pelos", "perto", "pessoas", "pode", "podem", "poder", "poderá",
    "podia", "pois", "ponto", "pontos", "por", "porém", "porque", "porquê", "posição", "possível",
    "pouca", "poucas", "pouco", "poucos", "primeira", "primeiro", "própria", "próprias", "próprio",
    "próprios", "próxima", "próximas", "próximo", "próximos", "puderam", "quais", "quão", "quando",
    "quanto", "quantos", "quarta", "quarto", "quatro", "que", "quem", "quer", "quereis", "querem",
    "queremas", "queres", "quero", "questão", "quinta", "quinto", "quinze", "relação", "sabe",
    "sabem", "são", "se", "segunda", "segundo", "sei", "seis", "seja", "sejam", "sejamos", "sem",
    "sempre", "sendo", "ser", "será", "serão", "serei", "seremos", "seria", "seriam", "seríamos",
    "sete", "seu", "seus", "sexta", "sexto", "sim", "sistema", "sob", "sobre", "sois", "somos",
    "sou", "sua", "suas", "tal", "talvez", "também", "tanta", "tantas", "tanto", "tantos", "te",
    "tem", "têm", "temos", "tendes", "tendo", "tenha", "tenham", "tenhamos", "tenho", "tens",
    "ter", "terá", "terão", "terceira", "terceiro", "terei", "teremos", "teria", "teriam",
    "teríamos", "teu", "teus", "toda", "todas", "todo", "todos", "trabalhar", "trabalho",
    "três", "treze", "tu", "tua", "tuas", "tudo", "última", "últimas", "último", "últimos",
    "um", "uma", "umas", "uns", "ver", "vez", "vezes", "ver", "vindo", "vinte", "você",
    "vocês", "vos", "vossa", "vossas", "vosso", "vossos", "zero"
}

import pandas as pd

def classificar_mensagens(df):
    # Definir períodos dos semestres
    datas_semestres = [
        ("2021/1", "2021-11-29", "2022-04-02"),
        ("2021/2", "2022-05-02", "2022-08-20"),
        ("2022/1", "2022-09-26", "2023-02-06"),
        ("2022/2", "2023-02-27", "2023-06-29"),
        ("2023/1", "2023-07-31", "2023-12-04"),
        ("2023/2", "2024-01-08", "2024-04-25"),
        ("2024/1", "2024-05-20", "2024-09-23"),
        ("2024/2", "2024-11-09", "2025-05-15")
    ]
    
    # Converter datas para datetime
    datas_semestres = [(s, pd.to_datetime(i), pd.to_datetime(f)) for s, i, f in datas_semestres]
    
    def classificar_mensagem(data):
        data = pd.to_datetime(data)  # Garantir que a data esteja no formato correto
        for semestre, inicio, fim in datas_semestres:
            if inicio <= data <= fim:
                return semestre
        return "Férias"
    
    def classificar_periodo(data):
        data = pd.to_datetime(data)
        for semestre, inicio, fim in datas_semestres:
            if inicio <= data <= fim:
                total_dias = (fim - inicio).days
                quartil_25 = inicio + pd.Timedelta(days=total_dias * 0.25)
                quartil_50 = inicio + pd.Timedelta(days=total_dias * 0.50)
                quartil_75 = inicio + pd.Timedelta(days=total_dias * 0.75)
                
                if data <= quartil_25:
                    return "25%"
                elif data <= quartil_50:
                    return "50%"
                elif data <= quartil_75:
                    return "75%"
                else:
                    return "100%"
        return "Férias"
    
    # Aplicar a classificação
    df['Semestre'] = df['Dia'].apply(classificar_mensagem)
    df['Periodo_Semestre'] = df['Dia'].apply(classificar_periodo)
    
    return df

import pandas as pd
import nltk
from textblob import TextBlob
from typing import Tuple

def analyze_sentiments(df: pd.DataFrame, text_column: str = 'Mensagem') -> Tuple[pd.DataFrame, dict]:
    """
    Realiza análise de sentimentos em um DataFrame com textos de conversas do WhatsApp.
    
    Args:
        df: DataFrame contendo os dados do chat
        text_column: Nome da coluna que contém os textos a serem analisados
        
    Returns:
        Tuple contendo:
        - DataFrame original com colunas adicionais de análise de sentimentos
        - Dicionário com estatísticas resumidas dos sentimentos
    """
    
    # Verificar se o DataFrame contém a coluna especificada
    if text_column not in df.columns:
        raise ValueError(f"A coluna '{text_column}' não existe no DataFrame")
    
    # Criar cópia para não modificar o original
    df_analysis = df.copy()
    
    # Função para limpeza do texto
    def clean_text(text):
        if not isinstance(text, str):
            return ""
        text = text.lower()
        text = nltk.RegexpTokenizer(r'\w+').tokenize(text)
        text = " ".join(word for word in text if word not in stopwords_pt)
        return text
    
    # Função para análise de sentimento
    def get_sentiment(text):
        analysis = TextBlob(text)
        return analysis.sentiment.polarity
    
    # Função para classificar o sentimento
    def classify_sentiment(polarity):
        if polarity > 0.1:  # Limiar ajustável
            return 'positivo'
        elif polarity < -0.1:  # Limiar ajustável
            return 'negativo'
        else:
            return 'neutro'
    
    # Aplicar as transformações
    df_analysis['texto_limpo'] = df_analysis[text_column].apply(clean_text)
    df_analysis['polaridade'] = df_analysis['texto_limpo'].apply(get_sentiment)
    df_analysis['sentimento'] = df_analysis['polaridade'].apply(classify_sentiment)
    
    # Calcular estatísticas resumidas
    sentiment_counts = df_analysis['sentimento'].value_counts().to_dict()
    stats = {
        'total_mensagens': len(df_analysis),
        'polaridade_media': df_analysis['polaridade'].mean(),
        'percent_positivo': (sentiment_counts.get('positivo', 0) / len(df_analysis)) * 100,
        'percent_negativo': (sentiment_counts.get('negativo', 0) / len(df_analysis)) * 100,
        'percent_neutro': (sentiment_counts.get('neutro', 0) / len(df_analysis)) * 100,
        'contagem_sentimentos': sentiment_counts
    }
    
    return df_analysis, stats
