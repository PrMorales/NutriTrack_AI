import streamlit as st
import pandas as pd
import datetime
import os

# Importações do Gemini com o nome completo do pacote
from google import genai 
from google.genai import types

# --- 1. CONFIGURAÇÃO DE SEGURANÇA E IA (AGORA GEMINI) ---
try:
    # Tenta ler a nova chave de API GEMINI
    chave_secreta = os.environ.get("GEMINI_API_KEY") 

    if not chave_secreta:
        st.error("Erro: A chave GEMINI_API_KEY não foi encontrada. Configure nos segredos do Streamlit Cloud.")
        st.stop()
        
    # Inicializa o cliente Gemini
    client = genai.Client(api_key=chave_secreta)
    
except Exception as e:
    st.error(f"Erro Fatal na Inicialização da API Gemini: {e}")
    st.stop()
    
# --- CONFIGURAÇÃO INICIAL DA PÁGINA ---
st.set_page_config(page_title="NutriTrack IA", layout="wide")
st.title("🥑 NutriTrack IA: Seu Assistente Nutricional Gemini")
st.caption("Migrado para a API gratuita do Google Gemini.")

# Inicializa o histórico do chat e o registro de refeições
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "model", "content": "Olá! Sou o NutriTrack IA. Posso te ajudar a registrar refeições e tirar dúvidas sobre nutrição. Qual seu objetivo de hoje?"}]

if "refeicoes" not in st.session_state:
    st.session_state.refeicoes = []

# --- FUNÇÃO DE CONVERSA COM A IA (AJUSTADA PARA GEMINI) ---
def conversar_com_ia(prompt):
    """Gera a resposta da IA como um especialista em nutrição usando o Gemini."""
    
    # 🌟 Definindo a Personalidade (System Instruction)
    system_instruction = (
        "Você é o NutriTrack AI, um assistente nutricional experiente e amigável. "
        "Suas respostas devem ser focadas em nutrição, dietas saudáveis, cálculo de calorias, "
        "e sugestões de receitas. Mantenha um tom profissional e de apoio. "
        "NUNCA forneça aconselhamento médico ou substitua um profissional de saúde."
    )
    
    # Mapeamento do histórico para o formato Gemini
    history = [
        types.Content(
            role="user" if m["role"] == "user" else "model", 
            parts=[types.Part.from_text(m["content"])]
        )
        for m in st.session_state.messages
    ]
    
    # Configurações do modelo
    config = types.GenerateContentConfig(
        system_instruction=system_instruction
    )

    # Chama a API do Gemini
    response = client.models.generate_content_stream(
        model='gemini-2.5-flash', # Modelo rápido e eficiente do Gemini
        contents=history + [types.Content(role="user", parts=[types.Part.from_text(prompt)])],
        config=config
    )
    return response

# ----------------------------------------------------
# LAYOUT E LÓGICA DE DADOS (Resto do código sem alterações)
# ----------------------------------------------------

col_chat, col_data = st.columns([2, 1])

with col_chat:
    st.header("💬 Bate-papo Nutricional")
    
    for message in st.session_state.messages:
        # Nota: O Gemini usa 'model' em vez de 'assistant'
        role = "assistant" if message["role"] == "model" else "user" 
        with st.chat_message(role):
            st.markdown(message["content"])

    if prompt := st.chat_input("O que você comeu ou qual sua dúvida?"):
        
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            response_stream = conversar_com_ia(prompt)
            full_response = st.write_stream(response_stream)
                
        # Salva a resposta do Gemini como 'model' no histórico
        st.session_state.messages.append({"role": "model", "content": full_response})

with col_data:
    st.header("📝 Rastreamento Diário")
    
    with st.form("registro_refeicao"):
        refeicao = st.selectbox("Tipo de Refeição", ["Café da Manhã", "Almoço", "Jantar", "Lanche", "Outro"])
        alimento = st.text_input("Qual alimento/prato?", placeholder="Ex: Omelete de queijo, Maçã")
        calorias = st.number_input("Calorias (kcal)", min_value=0, step=1)
        
        submit_button = st.form_submit_button("Adicionar Refeição")
        
        if submit_button and alimento:
            st.session_state.refeicoes.append({
                "Data": datetime.date.today(),
                "Tipo": refeicao,
                "Alimento": alimento,
                "Calorias": calorias
            })
            st.success(f"✅ {alimento} adicionado com sucesso!")
            
    st.markdown("---")
    
    if st.session_state.refeicoes:
        df = pd.DataFrame(st.session_state.refeicoes)
        df_hoje = df[df['Data'] == datetime.date.today()]
        
        st.subheader("Resumo de Hoje")
        total_calorias = df_hoje['Calorias'].sum()
        st.metric(label="Total de Calorias Consumidas", value=f"{total_calorias} kcal")
        
        st.subheader("Distribuição das Refeições")
        calorias_por_tipo = df_hoje.groupby('Tipo')['Calorias'].sum().sort_values(ascending=False)
        st.bar_chart(calorias_por_tipo)

    else:
        st.info("Comece a registrar suas refeições usando o formulário acima.")