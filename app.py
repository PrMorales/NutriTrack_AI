import streamlit as st
from openai import OpenAI
import pandas as pd
import datetime
# Não precisamos do 'import os' se estamos usando apenas st.secrets

# --- 1. CONFIGURAÇÃO DE SEGURANÇA E IA (Formato st.secrets) ---
try:
    # Tenta acessar a chave no formato padrão do Streamlit Secrets
    chave_secreta = st.secrets["external_api"]["openai_api_key"]
    client = OpenAI(api_key=chave_secreta)
except KeyError:
    # Tratamento de erro específico para a chave não ser encontrada
    st.error("Erro na configuração: A chave de API não foi encontrada. Configure [external_api] e openai_api_key nos segredos do Streamlit Cloud.")
    st.stop()
except Exception as e:
    st.error(f"Erro Fatal na Inicialização da API: {e}")
    st.stop()
    
# --- CONFIGURAÇÃO INICIAL DA PÁGINA E TÍTULOS ---
st.set_page_config(page_title="NutriTrack IA", layout="wide")
st.title("🥑 NutriTrack IA: Seu Assistente Nutricional Inteligente")
st.caption("Desenvolvido por PrMorales, usando Streamlit, OpenAI e Análise de Dados.")

# Inicializa o histórico do chat e o registro de refeições na sessão
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Olá! Sou o NutriTrack IA. Posso te ajudar a registrar refeições e tirar dúvidas sobre nutrição. Qual seu objetivo de hoje?"}]

if "refeicoes" not in st.session_state:
    st.session_state.refeicoes = []

# --- FUNÇÃO DE CONVERSA COM A IA ---
def conversar_com_ia(prompt):
    """Gera a resposta da IA como um especialista em nutrição."""
    system_prompt = (
        "Você é o NutriTrack AI, um assistente nutricional experiente e amigável. "
        "Suas respostas devem ser focadas em nutrição, dietas saudáveis, e sugestões de receitas. "
        "Mantenha um tom profissional e de apoio. NUNCA forneça aconselhamento médico."
    )
    
    messages_to_send = [{"role": "system", "content": system_prompt}]
    
    for message in st.session_state.messages:
        if message["role"] in ["user", "assistant"]:
            messages_to_send.append({"role": message["role"], "content": message["content"]})
            
    messages_to_send.append({"role": "user", "content": prompt})

    # Chama a API
    response = client.chat.completions.create(
        model="gpt-3.5-turbo", 
        messages=messages_to_send,
        stream=True
    )
    return response

# --- LAYOUT PRINCIPAL EM DUAS COLUNAS ---
col_chat, col_data = st.columns([2, 1])

# ----------------------------------------------------
# COLUNA 1: CHATBOT 
# ----------------------------------------------------
with col_chat:
    st.header("💬 Bate-papo Nutricional")
    
    # Exibir histórico de mensagens
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Capturar novo input do usuário
    if prompt := st.chat_input("O que você comeu ou qual sua dúvida?"):
        
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            response_stream = conversar_com_ia(prompt)
            full_response = st.write_stream(response_stream)
                
        st.session_state.messages.append({"role": "assistant", "content": full_response})


# ----------------------------------------------------
# COLUNA 2: REGISTRO DE DADOS E VISUALIZAÇÃO
# ----------------------------------------------------
with col_data:
    st.header("📝 Rastreamento Diário")
    
    # Formulário de registro de refeição
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
            st.success(f✔️ {alimento} adicionado com sucesso!")
            
    st.markdown("---")
    
    # Exibição e Análise de Dados (Seu MBA em Ação!)
    if st.session_state.refeicoes:
        df = pd.DataFrame(st.session_state.refeicoes)
        df_hoje = df[df['Data'] == datetime.date.today()]
        
        st.subheader("Resumo de Hoje")
        
        # Total de Calorias
        total_calorias = df_hoje['Calorias'].sum()
        st.metric(label="Total de Calorias Consumidas", value=f"{total_calorias} kcal")
        
        # Gráfico de Distribuição por Tipo de Refeição
        st.subheader("Distribuição das Refeições")
        calorias_por_tipo = df_hoje.groupby('Tipo')['Calorias'].sum().sort_values(ascending=False)
        st.bar_chart(calorias_por_tipo)

        # Tabela completa (opcional, para visualização detalhada)
        with st.expander("Ver Tabela Detalhada"):
            st.dataframe(df_hoje, use_container_width=True)

    else:
        st.info("Comece a registrar suas refeições usando o formulário acima.")