import streamlit as st
import os
import google.generativeai as genai
from google.generativeai import types
import pandas as pd
import datetime

# --- CONFIGURAÇÃO DE IA (LEITURA ROBUSTA) ---
try:
    chave_secreta = os.environ.get("GEMINI_API_KEY") 

    if not chave_secreta:
        st.error("Erro de Configuração: Chave GEMINI_API_KEY ausente.")
        st.stop()
        
    client = genai.Client(api_key=chave_secreta)
    
except Exception as e:
    st.error(f"Falha na Inicialização da API: {e}")
    st.stop()
    
# --- CONFIGURAÇÃO INICIAL DA PÁGINA ---
st.set_page_config(page_title="NutriTrack IA - Vegetariano", layout="wide")

# Estilo para UI limpa
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .st-emotion-cache-1r6r8qj {max-width: 800px;}
    </style>
    """, unsafe_allow_html=True)

st.title("🌱 NutriTrack IA: Análise Vegetariana Inteligente")
st.subheader("Informe sua refeição e receba a análise e dicas!")

# Inicializa o histórico do chat
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "model", "content": "Olá! Eu sou seu assistente NutriTrack IA. Diga-me o que comeu para receber a análise nutricional e dicas vegetarianas."}
    ]

# --- FUNÇÃO DE CONVERSA COM A IA ---
def conversar_com_ia(prompt):
    
    # INSTRUÇÃO DETALHADA PARA FORÇAR A SAÍDA EM TABELA E DAR DICAS VEGETARIANAS
    system_instruction = (
        "Você é o NutriTrack AI, um especialista em nutrição focado em dietas vegetarianas. "
        "1. Analise o alimento ou refeição fornecida pelo usuário. "
        "2. Retorne uma tabela formatada em MARKDOWN com 7 colunas (Calorias, Açúcar, Vitamina C, Proteína, Ferro, Carboidratos, Gorduras). Use valores estimados e unidades. "
        "3. Sempre adicione uma breve dica de alimentação focada em vegetarianos, especialmente sobre como obter nutrientes como Ferro e Proteína."
        "4. Mantenha um tom profissional."
    )
    
    # 1. Adiciona a instrução do sistema
    contents_to_send = [
        types.Content(
            role="user",
            parts=[types.Part.from_text(system_instruction)]
        )
    ]
    
    # 2. Adiciona a mensagem atual do usuário
    contents_to_send.append(
        types.Content(role="user", parts=[types.Part.from_text(prompt)])
    )

    # Chama a API do Gemini
    response = client.models.generate_content_stream(
        model='gemini-2.5-flash',
        contents=contents_to_send
    )
    return response

# ----------------------------------------------------
# INTERFACE PRINCIPAL: CHATBOT
# ----------------------------------------------------

# Exibir histórico de mensagens
for message in st.session_state.messages:
    # Mapeia a role 'model' (Gemini) para 'assistant' (Streamlit)
    role = "assistant" if message["role"] == "model" else "user" 
    with st.chat_message(role):
        st.markdown(message["content"])

# Capturar novo input do usuário
if prompt := st.chat_input("Ex: 'Sanduíche de pasta de amendoim com banana'"):
    
    # 1. Exibir input do usuário
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 2. Gerar e exibir resposta da IA (streaming)
    with st.chat_message("assistant"):
        with st.spinner("Analisando refeição e gerando tabela nutricional..."):
            try:
                response_stream = conversar_com_ia(prompt)
                full_response = st.write_stream(response_stream)
            except Exception as e:
                # Exibe o erro amigável
                st.error("Erro na comunicação com a IA. Tente novamente ou verifique sua chave GEMINI_API_KEY.")
                full_response = "Erro de API." 
        
    # 3. Adicionar resposta completa ao histórico
    st.session_state.messages.append({"role": "model", "content": full_response})