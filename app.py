import streamlit as st
from dotenv import load_dotenv
load_dotenv()
from utils import setup_app, get_ai_agent, show_sidebar, get_img_as_base64
from auth import login_with_google, check_authentication, logout
from database import get_database
import os

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
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # Images side by side, vertically centered
        img_col1, img_col2 = st.columns([0.8, 1.2], vertical_alignment="center")
        with img_col1:
            if os.path.exists("assets/mascot.png"):
                st.image("assets/mascot.png", width=200)
        with img_col2:
            if os.path.exists("assets/logo_matemai.png"):
                st.image("assets/logo_matemai.png", use_container_width=True)
            
        # Check for OAuth Callback (Code in URL)
        if "code" in st.query_params:
            login_with_google()
            
        st.markdown('<p class="login-title" style="font-size: 3rem;">O jeito grátis, divertido e eficaz de aprender matemática!</p>', unsafe_allow_html=True)
        # Get Login URL
        from auth import get_login_url
        login_url = get_login_url()
        
        # Custom Buttons Side by Side (Centered)
        # Using columns to create spacing: [spacer, btn1, btn2, spacer]
        c1, c2, c3, c4 = st.columns([1, 4, 4, 1])
        
        if login_url:
            with c2:
                # CRIAR UMA CONTA (Gray as requested)
                st.link_button("CRIAR UMA CONTA", login_url)
            
            with c3:
                # JÁ TENHO UMA CONTA (Blue)
                st.link_button("JÁ TENHO UMA CONTA", login_url, type="primary")
        else:
            st.error("Erro ao configurar login. Verifique as credenciais.")

        # Banner com Link (Agora em baixo)
        st.markdown("---")
        st.markdown("""
            <a href="https://docs.google.com/forms/d/e/1FAIpQLSeIjjqbB1khH8BYm5wbQkI6dOIb797ovGQGdz-WjzdvfTaeeQ/viewform" target="_blank">
                <img src="data:image/png;base64,{}" style="width: 100%; border-radius: 15px; margin-top: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); transition: transform 0.3s;">
            </a>
            <style>
            img:hover {{
                transform: scale(1.02);
            }}
            </style>
        """.format(get_img_as_base64("assets/banner_pesquisa.png").split(",")[1]), unsafe_allow_html=True)
    
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
