import streamlit as st
import os
from google import genai
from google.genai import types
import pandas as pd
import datetime
# (Não precisamos mais de 'import time')

st.set_page_config(page_title="Teste API", layout="wide")

try:
    chave_secreta = os.environ.get("GEMINI_API_KEY")

    if not chave_secreta:
        st.error("ERRO: Chave GEMINI_API_KEY ausente.")
        st.stop()

    # Tenta inicializar o cliente
    client = genai.Client(api_key=chave_secreta)

    # Tenta a comunicação mais simples: listar modelos
    modelos = client.models.list()
    
    st.title("✅ SUCESSO DE COMUNICAÇÃO COM O GEMINI!")
    st.success("O aplicativo conseguiu listar os modelos da API do Gemini. A comunicação está OK!")
    st.write("Um dos modelos disponíveis:", next(iter(modelos)).name)

except Exception as e:
    st.title("❌ FALHA CRÍTICA DE COMUNICAÇÃO")
    st.error(f"Erro: O Streamlit não conseguiu se comunicar com a API do Gemini. Causa mais provável: Chave inválida ou problema de rede. Erro: {e}")

# O restante do código NÃO PRECISA ESTAR AQUI DURANTE ESTE TESTE.