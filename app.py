import streamlit as st
from utils import setup_app, get_ai_agent, show_sidebar
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
setup_app()

# Authentication Check
if not check_authentication():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # Images side by side, vertically centered
        img_col1, img_col2 = st.columns([0.8, 1.2], vertical_alignment="center")
        with img_col1:
            st.image("assets/mascot.png", width=200)
        with img_col2:
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
                # COMECE AGORA (Gray as requested)
                st.link_button("COMECE AGORA", login_url)
            
            with c3:
                # JÁ TENHO UMA CONTA (Blue)
                st.link_button("JÁ TENHO UMA CONTA", login_url, type="primary")
        else:
            st.error("Erro ao configurar login. Verifique as credenciais.")
            
        # Apply custom classes to buttons via JavaScript hack or just rely on Streamlit's limited styling for now + CSS injection
        st.markdown("""
        <style>
        /* Base Style for All Link Buttons */
        div[data-testid="stLinkButton"] > a {
            width: 100%;
            border-radius: 15px;
            height: 60px;
            font-weight: 800;
            text-transform: uppercase;
            font-size: 1.1rem;
            display: flex;
            align-items: center;
            justify-content: center;
            text-decoration: none;
            transition: all 0.1s ease;
            box-shadow: 0px 4px 0px rgba(0,0,0,0.2); /* 3D Effect Base */
            border: none;
            margin-bottom: 4px; /* Space for shadow */
        }
        
        /* Hover Effect (Pressed) */
        div[data-testid="stLinkButton"] > a:active, 
        div[data-testid="stLinkButton"] > a:hover:active {
            transform: translateY(4px);
            box-shadow: 0px 0px 0px rgba(0,0,0,0.2); /* Shadow disappears */
            margin-bottom: 0px;
            margin-top: 4px;
        }

        /* 1. COMECE AGORA (Gray) - Column 2 */
        div[data-testid="stColumn"]:nth-of-type(2) div[data-testid="stLinkButton"] > a {
            background-color: #e5e5e5;
            color: #afafaf !important; /* Text color for gray button */
            color: #4b4b4b !important;
        }
        div[data-testid="stColumn"]:nth-of-type(2) div[data-testid="stLinkButton"] > a:hover {
            background-color: #d4d4d4;
            color: #4b4b4b !important;
        }

        /* 2. JÁ TENHO UMA CONTA (Blue) - Column 3 */
        div[data-testid="stColumn"]:nth-of-type(3) div[data-testid="stLinkButton"] > a {
            background-color: #0047AB;
            color: white !important;
        }
        div[data-testid="stColumn"]:nth-of-type(3) div[data-testid="stLinkButton"] > a:hover {
            background-color: #0056b3;
            color: white !important;
        }
        </style>
        """, unsafe_allow_html=True)
    st.stop() # Stop execution if not logged in

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
