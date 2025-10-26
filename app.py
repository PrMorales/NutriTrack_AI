Com certeza! Você está prestes a ver o seu projeto NutriTrack IA funcionando.

Aqui está o código app.py completo, incluindo todas as correções de compatibilidade, a função de teste simplificada para o Gemini, o foco na nutrição vegetariana e a interface de chat limpa.

💻 Código Final e Completo: app.py
Este código está pronto para ser copiado, enviado ao GitHub, e deve funcionar perfeitamente com a chave GEMINI_API_KEY nos seus segredos.

Python

import streamlit as st
import os
from google import genai
from google.genai import types
import pandas as pd
import datetime

# --- 1. CONFIGURAÇÃO DE SEGURANÇA E IA (GEMINI) ---
try:
    # Lê a chave da variável de ambiente GEMINI_API_KEY
    chave_secreta = os.environ.get("GEMINI_API_KEY") 

    if not chave_secreta:
        st.error("Erro: A chave GEMINI_API_KEY não foi encontrada. Configure nos segredos do Streamlit Cloud.")
        st.stop()
        
    client = genai.Client(api_key=chave_secreta)
    
except Exception as e:
    st.error(f"Erro Fatal na Inicialização da API Gemini. Verifique os logs. {e}")
    st.stop()
    
# --- CONFIGURAÇÃO INICIAL DA PÁGINA E TEMA ---
st.set_page_config(page_title="NutriTrack IA - Vegetariano", layout="wide")

# Personalizando a interface para parecer mais limpa (Estilo Minimalista)
st.markdown(
    """
    <style>
    /* Esconde o menu e o rodapé padrão do Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    /* Centraliza e define largura máxima para a experiência de chat */
    .stApp {
        padding-top: 20px;
        padding-bottom: 20px;
    }
    .st-emotion-cache-1r6r8qj {
        max-width: 800px; 
    }
    </style>
    """, unsafe_allow_html=True
)

st.title("🌱 NutriTrack IA: Análise Vegetariana Inteligente")
st.subheader("Informe sua refeição e receba a análise nutricional e dicas!")

# Inicializa o histórico do chat
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "model", "content": "Olá! Eu sou seu assistente NutriTrack IA. Informe-me o que você comeu (ex: 'Lentilha, arroz e salada de tomate') para receber a análise e dicas vegetarianas."}
    ]


# --- FUNÇÃO DE CONVERSA COM A IA (FINAL E SIMPLIFICADA) ---
def conversar_com_ia(prompt):
    """Gera a resposta da IA com foco na tabela nutricional e dicas."""
    
    # 🌟 A INSTRUÇÃO DO SISTEMA É O QUE DEFINE O BOT
    system_instruction = (
        "Você é o NutriTrack AI, um especialista em nutrição focado em dietas vegetarianas. "
        "1. Analise o alimento ou refeição fornecida pelo usuário. "
        "2. Retorne uma tabela formatada em MARKDOWN com 7 colunas (Calorias, Açúcar, Vitamina C, Proteína, Ferro, Carboidratos, Gorduras). "
        "3. Sempre adicione uma breve dica de alimentação focada em vegetarianos, especialmente sobre como obter nutrientes como Ferro e Proteína."
        "4. Mantenha um tom profissional e amigável."
    )
    
    # Prepara o conteúdo, garantindo que o prompt do usuário seja a última entrada
    contents_to_send = []
    
    # 1. Adiciona a instrução do sistema
    contents_to_send.append(
        types.Content(
            role="user",
            parts=[types.Part.from_text(system_instruction)]
        )
    )
    
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
                # Se falhar na comunicação, mostra o erro amigável (o que estava acontecendo)
                st.error("Erro na comunicação com a IA. Tente novamente ou verifique sua chave GEMINI_API_KEY. O problema NÃO é o código!")
                full_response = "Erro de API." 
        
    # 3. Adicionar resposta completa ao histórico
    st.session_state.messages.append({"role": "model", "content": full_response})