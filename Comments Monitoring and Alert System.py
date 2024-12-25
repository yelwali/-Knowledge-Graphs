import streamlit as st
import pandas as pd
import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from textblob import TextBlob
import spacy

alerts = []
# Charger le modèle SpaCy
nlp = spacy.load("en_core_web_sm")

# Liste de mots-clés suspects
suspicious_keywords = ["attack", "bomb", "terrorist", "kill", "explosion", "radical", "jihad", "violence", "threat"]

# Fonction pour extraire les entités d'une phrase
def get_entities(sent):
    ent1 = ""
    ent2 = ""
    prv_tok_dep = ""
    prv_tok_text = ""
    prefix = ""
    modifier = ""

    for tok in nlp(sent):
        if tok.dep_ != "punct":
            if tok.dep_ == "compound":
                prefix = tok.text
                if prv_tok_dep == "compound":
                    prefix = prv_tok_text + " " + tok.text

            if tok.dep_.endswith("mod"):
                modifier = tok.text
                if prv_tok_dep == "compound":
                    modifier = prv_tok_text + " " + tok.text

            if tok.dep_.find("subj") != -1:
                ent1 = modifier + " " + prefix + " " + tok.text
                prefix = ""
                modifier = ""

            if tok.dep_.find("obj") != -1:
                ent2 = modifier + " " + prefix + " " + tok.text

            prv_tok_dep = tok.dep_
            prv_tok_text = tok.text

    return [ent1.strip(), ent2.strip()]

# Fonction pour extraire la relation d'une phrase
def get_relation(sent):
    doc = nlp(sent)
    for token in doc:
        if token.dep_ == "ROOT":
            return token.text
    return ""

# Fonction pour analyser les sentiments
def analyze_behavior(comment):
    analysis = TextBlob(comment)
    polarity = analysis.sentiment.polarity
    if polarity > 0:
        return "Positive"
    elif polarity < 0:
        return "Negative"
    else:
        return "Neutral"

# Fonction pour détecter le contenu suspect
def detect_suspicious_content(comment):
    for word in suspicious_keywords:
        if word.lower() in comment.lower():
            return True
    return False

# Titre de l'application
st.markdown(
    """
    <div style="
        background-color: #f9f9f9;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1);
    ">
        <h1 style="
            color: #FF5733; 
            font-family: Arial, sans-serif; 
            background: -webkit-linear-gradient(45deg, #FF5733, #FFC300);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
        ">
            Comments Monitoring and Alert System
        </h1>
    </div>
    """,
    unsafe_allow_html=True
)
# Charger un fichier CSV
st.sidebar.markdown(
    """
    <div style="
        background-color: #FF5733;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    ">
        <h2 style="
            color: white; 
            font-family: Arial, sans-serif; 
            font-weight: bold;
            text-shadow: 2px 2px 3px rgba(0, 0, 0, 0.3);
        ">
            Load the Data
        </h2>
    </div>
    """,
    unsafe_allow_html=True
)

# Ligne de séparation
st.sidebar.markdown(
    """
    <hr style="
        border: none;
        height: 2px;
        background-color: #FF5733;
        margin: 20px 0;
    ">
    """,
    unsafe_allow_html=True
)

# Section 2 : Import a CSV File
st.sidebar.markdown(
    """
    <div style="
        background-color: #008080; 
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1);
    ">
        <h3 style="
            color: white; 
            font-family: 'Arial', sans-serif; 
            font-weight: bold; 
            text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.3);
        ">
            Import a CSV File Containing the Comments
        </h3>
    </div>
    """,
    unsafe_allow_html=True
)
# File uploader
uploaded_file = st.sidebar.file_uploader("", type=["csv"])
if uploaded_file:
    # Lecture des données
    data = pd.read_csv(uploaded_file)
    dataset = data[['Comment_Author', 'Comment_Body']].dropna()

    # Analyse des données
    st.sidebar.markdown(
    """
    <hr style="
        border: none;
        height: 2px;
        background-color: #FF5733;
        margin: 20px 0;
    ">
    """,
    unsafe_allow_html=True
)
    st.markdown(
    """
    <div style="
        background-color: #1E90FF; 
        padding: 10px; 
        border-radius: 10px; 
        text-align: center; 
        margin-bottom: 15px;
    ">
        <h3 style="
            color: white; 
            font-family: Arial, sans-serif; 
            text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.2);
        ">
            Comments Table
        </h3>
    </div>
    """,
    unsafe_allow_html=True
)
    st.dataframe(dataset)

    entity_pairs = []
    sentiments = []
    alerts = []

    st.markdown(
    """
    <div style="
        background-color: #1E90FF; 
        padding: 10px; 
        border-radius: 10px; 
        text-align: center; 
        margin-bottom: 15px;
    ">
        <h3 style="
            color: white; 
            font-family: 'Arial', sans-serif; 
            font-weight: bold; 
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
        ">
            Entity Relation Extraction and Comment Analysis
        </h3>
    </div>
    """,
    unsafe_allow_html=True
)
    for _, row in dataset.iterrows():
        author = row['Comment_Author']
        comment = row['Comment_Body']

        # Extraction des entités et des relations
        entities = get_entities(comment)
        relation = get_relation(comment)

        # Analyse des sentiments
        sentiment = analyze_behavior(comment)

        # Détection de contenu suspect
        is_suspicious = detect_suspicious_content(comment)

        # Stockage des résultats
        entity_pairs.append((author, entities[0], entities[1], relation))
        sentiments.append(sentiment)

        # Détection des alertes
        if is_suspicious and sentiment == "Negative":
            alerts.append((author, comment, relation, sentiment, is_suspicious))

    # Création du DataFrame des entités et relations
    results_df = pd.DataFrame(entity_pairs, columns=['Author', 'Entity1', 'Entity2', 'Relation'])
    results_df['Sentiment'] = sentiments
    st.dataframe(results_df)


    

    # Filter "see" and "need" relations
    see_df = results_df[results_df['Relation'].str.contains("see", case=False, na=False)]
    need_df = results_df[results_df['Relation'].str.contains("need", case=False, na=False)]
    # Visualize the first graph (relation "see")
    st.markdown(
    """
    <div style="
        background-color: #FF4500; 
        padding: 10px; 
        border-radius: 10px; 
        text-align: center; 
        margin-bottom: 15px;
    ">
        <h3 style="
            color: white; 
            font-family: 'Arial', sans-serif; 
            font-weight: bold; 
            text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.3);
        ">
            Graph for 'see' Relations
        </h3>
    </div>
    """,
    unsafe_allow_html=True
)
    kg_see_df = see_df[["Entity1", "Entity2", "Relation"]].dropna()
    G_see = nx.from_pandas_edgelist(kg_see_df, "Entity1", "Entity2", edge_attr=True, create_using=nx.MultiDiGraph())
    plt.figure(figsize=(12, 8))
    pos_see = nx.spring_layout(G_see)
    nx.draw(G_see, pos_see, with_labels=True, node_size=3000, node_color="skyblue", font_size=15, font_color="black", font_weight="bold", alpha=0.7)
    st.pyplot(plt)

    # Visualize the second graph (relation "need")
    st.markdown(
    """
    <div style="
        background-color: #FF4500; 
        padding: 10px; 
        border-radius: 10px; 
        text-align: center; 
        margin-bottom: 15px;
    ">
        <h3 style="
            color: white; 
            font-family: 'Arial', sans-serif; 
            font-weight: bold; 
            text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.3);
        ">
            Graph for 'need' Relations
        </h3>
    </div>
    """,
    unsafe_allow_html=True
)
    kg_need_df = need_df[["Entity1", "Entity2", "Relation"]].dropna()
    G_need = nx.from_pandas_edgelist(kg_need_df, "Entity1", "Entity2", edge_attr=True, create_using=nx.MultiDiGraph())
    plt.figure(figsize=(12, 8))
    pos_need = nx.spring_layout(G_need)
    nx.draw(G_need, pos_need, with_labels=True, node_size=3000, node_color="lightgreen", font_size=15, font_color="black", font_weight="bold", alpha=0.7)
    st.pyplot(plt)

    # Affichage des alertes en temps réel
    st.markdown(
    """
    <div style="
        background-color: #FF0000; 
        padding: 15px; 
        border-radius: 10px; 
        text-align: center; 
        box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.2);
        margin-bottom: 20px;
    ">
        <h3 style="
            color: white; 
            font-family: 'Arial', sans-serif; 
            font-weight: bold; 
            text-shadow: 1px 1px 4px rgba(0, 0, 0, 0.3);
        ">
            Real-time Alerts 🚨
        </h3>
    </div>
    """,
    unsafe_allow_html=True
)
if alerts:
    for alert in alerts:
        author, comment, relation, sentiment, is_suspicious = alert
        
        # Afficher uniquement si le contenu est suspect
        if is_suspicious and sentiment =='Negative':
            reason = "Contenu suspect"
            st.error(f"🚨 Alerte : Auteur: {author}, "
                     f"Relation: {relation}, Sentiment: {sentiment}, Raison: {reason}")
else:
    st.success("**No alerts detected.**")

# Message pour inviter à importer un fichier CSV
st.info("**Please import a CSV file to get started.**")


