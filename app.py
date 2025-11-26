import streamlit as st
from dotenv import load_dotenv
load_dotenv()
from utils import setup_app, get_ai_agent, show_sidebar, get_img_as_base64
from auth import login_with_google, check_authentication, logout
from database import get_database

# Page Config
st.set_page_config(
    page_title="Matemai",
    page_icon="🧮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load Custom CSS
def local_css(file_name):
    with open(file_name, encoding='utf-8') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

try:
    local_css("assets/style.css")
    local_css("assets/loading.css")
except FileNotFoundError:
    pass 
# Initialize Session State
setup_app(is_public_page=True)

# Authentication Check
if not check_authentication():
    # Main Layout
    col1, col2 = st.columns([1, 1])

    with col1:
        # Banner com Link
        st.markdown("""
            <a href="https://docs.google.com/forms/d/e/1FAIpQLSeIjjqbB1khH8BYm5wbQkI6dOIb797ovGQGdz-WjzdvfTaeeQ/viewform" target="_blank">
                <img src="data:image/png;base64,{}" style="width: 100%; border-radius: 15px; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); transition: transform 0.3s;">
            </a>
            <style>
            img:hover {{
                transform: scale(1.02);
            }}
            </style>
        """.format(get_img_as_base64("assets/banner_pesquisa.png").split(",")[1]), unsafe_allow_html=True)

        st.markdown("<h1 style='font-size: 3rem; margin-bottom: 0;'>Matem<span style='color: #0047AB;'>AI</span></h1>", unsafe_allow_html=True)
        st.markdown("### O jeito grátis, divertido e eficaz de aprender matemática!")
        
        st.markdown("---")
        
        # Login Buttons
        c1, c2 = st.columns(2)
        with c1:
            if st.button("CRIAR UMA CONTA", type="secondary", use_container_width=True):
                login_with_google()
                
        with c2:
            if st.button("JÁ TENHO UMA CONTA", type="primary", use_container_width=True):
                login_with_google()
    
    # Stop execution if not logged in
    st.stop()


# Sidebar
# Sidebar
show_sidebar()

# --- Main Content ---

# 1. Hero Section & Stats
st.title("🏠 Início")

# Get User Stats for Dashboard
st.cache_resource.clear() # Force reload of database instance to get new methods
db = get_database()
user_email = st.session_state.user_profile['email']
current_xp = st.session_state.xp
user_rank = db.get_user_rank(user_email, current_xp)

# Stats Dashboard
st.markdown("### 📊 Seu Desempenho")
stat_col1, stat_col2, stat_col3 = st.columns(3)

with stat_col1:
    st.container(border=True).metric("🏆 XP Total", f"{current_xp}", delta="Continue assim!")
with stat_col2:
    st.container(border=True).metric("📚 Nível Atual", f"{st.session_state.level}", delta="Mestre da Matemática")
with stat_col3:
    st.container(border=True).metric("🌍 Ranking Global", f"#{user_rank}", delta="Top Alunos")

st.divider()

# 2. AI Greeting
st.markdown(f"### 👋 Olá, {st.session_state.user_profile['name']}!")

agent = get_ai_agent()
if "greeting" not in st.session_state:
    with st.spinner("O MatemAI está escrevendo uma mensagem para você..."):
        try:
            st.session_state.greeting = agent.generate_greeting(st.session_state.user_profile['name'])
        except AttributeError:
            st.cache_resource.clear()
            agent = get_ai_agent()
            st.session_state.greeting = agent.generate_greeting(st.session_state.user_profile['name'])

st.info(f"🤖 **MatemAI diz:**\n\n{st.session_state.greeting}")

# Quick Action Buttons
st.markdown("""
<style>
/* Estilo para os botões de ação rápida */
div.stButton > button {
    height: 70px;
    font-size: 22px !important;
    font-weight: bold !important;
    border-radius: 15px !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    text-transform: uppercase;
}
div.stButton > button:hover {
    transform: translateY(-3px);
    box-shadow: 0 6px 12px rgba(0,0,0,0.2);
}
/* Destaque especial para o botão primário (Desafio) */
div.stButton > button[kind="primary"] {
    background: linear-gradient(45deg, #0047AB, #00BFFF) !important;
    border: none !important;
    animation: pulse-action 2s infinite;
}
@keyframes pulse-action {
    0% { box-shadow: 0 0 0 0 rgba(0, 191, 255, 0.7); }
    70% { box-shadow: 0 0 0 10px rgba(0, 191, 255, 0); }
    100% { box-shadow: 0 0 0 0 rgba(0, 191, 255, 0); }
}
</style>
""", unsafe_allow_html=True)

col_action1, col_action2 = st.columns(2)

with col_action1:
    if st.button("👤 Atualizar Perfil", use_container_width=True):
        st.switch_page("pages/1_Meu_Perfil.py")

with col_action2:
    if st.button("🚀 REALIZAR MEU DESAFIO", type="primary", use_container_width=True):
        st.switch_page("pages/2_Desafios_Gamificados.py")

st.divider()

# 3. About MatemAI
st.markdown("### 🚀 O que é o MatemAI?")
st.markdown("""
O **MatemAI** é sua plataforma inteligente para dominar a matemática! 
Aqui você aprende de forma personalizada, cumpre missões divertidas e compete com outros estudantes.

*   **🧠 IA Personalizada:** O conteúdo se adapta ao seu ritmo.
*   **🎮 Gamificação:** Ganhe XP, suba de nível e desbloqueie conquistas.
*   **📅 Organização:** Mantenha seus estudos em dia com a Agenda Inteligente.
""")

st.divider()

# 4. Quick Actions (Interactive Cards)
st.markdown("### 🎯 O que você quer fazer agora?")

act_col1, act_col2 = st.columns(2)
act_col3, act_col4 = st.columns(2)

with act_col1:
    with st.container(border=True):
        st.markdown("#### 👤 Meu Perfil")
        st.write("Atualize seus dados e preferências de aprendizado.")
        st.page_link("pages/1_Meu_Perfil.py", label="Ir para Perfil", icon="✏️", use_container_width=True)

with act_col2:
    with st.container(border=True):
        st.markdown("#### 🎮 Desafios")
        st.write("Complete missões diárias e ganhe muito XP!")
        st.page_link("pages/2_Desafios_Gamificados.py", label="Jogar Agora", icon="🚀", use_container_width=True)

with act_col3:
    with st.container(border=True):
        st.markdown("#### 🏆 Ranking")
        st.write("Veja sua posição e compare com os amigos.")
        st.page_link("pages/5_Ranking.py", label="Ver Ranking", icon="🥇", use_container_width=True)

with act_col4:
    with st.container(border=True):
        st.markdown("#### 📅 Agenda")
        st.write("Organize sua rotina e não perca o foco.")
        st.page_link("pages/4_Agenda_de_Estudos.py", label="Ver Agenda", icon="📅", use_container_width=True)
