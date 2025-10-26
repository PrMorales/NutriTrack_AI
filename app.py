import streamlit as st
from openai import OpenAI
import pandas as pd
import datetime
import os # Importação necessária para usar os.environ

# --- 1. CONFIGURAÇÃO DE SEGURANÇA E IA ---
try:
    # Tenta ler a chave de API da variável de ambiente simples, que é o formato
    # que o Streamlit Cloud aceita com mais facilidade.
    chave_secreta = os.environ.get("OPENAI_API_KEY") 

    if not chave_secreta:
        # Se a chave não for encontrada na variável de ambiente
        st.error("Erro: A chave de API não foi encontrada. Configure OPENAI_API_KEY nos segredos do Streamlit Cloud.")
        st.stop()

    client = OpenAI(api_key=chave_secreta)

except Exception as e:
    st.error(f"Erro Fatal na Inicialização da API: {e}")
    st.stop()

# --- CONFIGURAÇÃO INICIAL DA PÁGINA (o código continua daqui) ---
st.set_page_config(page_title="NutriTrack IA", layout="wide")
# ...