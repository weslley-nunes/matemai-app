import streamlit as st
from utils import get_ai_methodology, setup_app, show_sidebar, render_avatar, save_user_progress
from avatar_assets import AVATAR_ASSETS, get_avatar_url
from database import get_database

# Initialize Session State
setup_app(requires_profile=False)
show_sidebar()

st.title("👤 Meu Perfil")

if "profile_redirect_reason" in st.session_state:
    st.warning(st.session_state.profile_redirect_reason)
    del st.session_state.profile_redirect_reason

if not st.session_state.user_profile:
    st.warning("Por favor, faça login na página inicial para acessar seu perfil.")
    st.stop()

if st.session_state.user_profile and st.session_state.user_profile.get("methodology"):
    st.info(f"Metodologia Atual: **{st.session_state.user_profile['methodology']}**")
    st.info("Você pode atualizar seus dados abaixo para recalcular sua metodologia.")

st.write("Personalize seu perfil para o Agente de IA adaptar o ensino.")
st.markdown("---")

# --- Avatar Studio Section ---
st.header("🎨 Estúdio de Criação de Avatar")

col_preview, col_wardrobe = st.columns([1, 2])

# Initialize avatar config in session state if not exists
if "avatar_config" not in st.session_state:
    # Try to load from profile first
    if st.session_state.user_profile and st.session_state.user_profile.get("avatar_config"):
        st.session_state.avatar_config = st.session_state.user_profile.get("avatar_config").copy()
    else:
        # Default config
        from utils import get_default_avatar_config
        st.session_state.avatar_config = get_default_avatar_config()

# Validate and Repair Config (Robust Fallback)
from utils import get_default_avatar_config
if not st.session_state.avatar_config or not isinstance(st.session_state.avatar_config, dict):
    st.session_state.avatar_config = get_default_avatar_config()
else:
    # Ensure all keys exist AND values are valid assets
    default = get_default_avatar_config()
    for k, v in default.items():
        # 1. Missing keys
        if k not in st.session_state.avatar_config:
            st.session_state.avatar_config[k] = v
        
        # 2. Invalid values (orphan IDs)
        # Check if the current value exists in AVATAR_ASSETS for this category
        # If the category exists in assets (some keys like 'mouth' match directly)
        if k in AVATAR_ASSETS:
            valid_ids = [item["id"] for item in AVATAR_ASSETS[k]]
            current_val = st.session_state.avatar_config[k]
            if current_val not in valid_ids:
                # Value not found in valid assets (e.g. old deprecated id), reset to default
                st.session_state.avatar_config[k] = v
    
    # 3. Remove unknown keys (garbage cleanup)
    keys_to_remove = [k for k in st.session_state.avatar_config.keys() if k not in default]
    for k in keys_to_remove:
        del st.session_state.avatar_config[k]

# Current Level
user_level = st.session_state.level

with col_wardrobe:
    st.subheader("Guarda-Roupa")
    
    # Categories to edit
    categories = {
        "Pele": "skinColor",
        "Cabelo/Chapéu": "top",
        "Cor do Cabelo": "hairColor",
        "Roupas": "clothing",
        "Cor da Roupa": "clothesColor",
        "Olhos": "eyes",
        "Sobrancelhas": "eyebrows",
        "Boca": "mouth",
        "Acessórios": "accessories"
    }
    
    # Create tabs for categories to organize UI
    cat_tabs = st.tabs(list(categories.keys()))
    
    for i, (cat_name, cat_key) in enumerate(categories.items()):
        with cat_tabs[i]:
            assets = AVATAR_ASSETS.get(cat_key, [])
            
            # Grid layout for items
            cols = st.columns(3)
            for idx, item in enumerate(assets):
                # Check if item is unlocked by level OR owned in inventory
                is_owned = False
                if "inventory" in st.session_state and item["id"] in st.session_state.inventory:
                    is_owned = True
                    
                is_locked = (item["level"] > user_level) and not is_owned
                
                with cols[idx % 3]:
                    # Visual indicator for selection
                    is_selected = st.session_state.avatar_config.get(cat_key) == item["id"]
                    
                    btn_label = f"{item['name']}"
                    if is_locked:
                        btn_label = f"🔒 Lvl {item['level']}"
                    elif is_selected:
                        btn_label = f"✅ {item['name']}"
                    elif is_owned and item["level"] > user_level:
                         btn_label = f"🔓 {item['name']}" # Show unlocked icon for purchased items
                        
                    # Button logic
                    if st.button(
                        btn_label, 
                        key=f"btn_{cat_key}_{item['id']}", 
                        disabled=is_locked,
                        use_container_width=True,
                        type="primary" if is_selected else "secondary"
                    ):
                        st.session_state.avatar_config[cat_key] = item["id"]
                        st.rerun()
                        
with col_preview:
    st.subheader("Visualização")
    
    # Generate URL
    avatar_url = get_avatar_url(st.session_state.avatar_config)
    
    # Display Avatar
    try:
        # Center the image using columns
        c_spacer1, c_img, c_spacer2 = st.columns([1, 4, 1])
        with c_img:
            render_avatar(avatar_url, width=250)
    except Exception as e:
        st.error(f"Erro ao carregar imagem: {e}")
    
    # Save Button
    if st.button("💾 Salvar Avatar", type="primary", use_container_width=True):
        with st.spinner("Salvando novo visual..."):
            db = get_database()
            email = st.session_state.user_profile.get("email")
            if db.save_avatar_config(email, st.session_state.avatar_config, avatar_url):
                # Update local session state
                st.session_state.user_profile["avatar"] = avatar_url
                st.session_state.user_profile["avatar_config"] = st.session_state.avatar_config
                st.success("Avatar atualizado com sucesso!")
                st.balloons()
                # Rerun to update sidebar
                import time
                time.sleep(1)
                st.rerun()
            else:
                st.error("Erro ao salvar avatar.")

    # --- Avatar Reset Section (Emergency Fix) ---
    st.markdown("---")
    if st.checkbox("🔧 Problemas com o Avatar? Clique aqui"):
        st.warning("Isso irá apagar seu avatar atual e restaurar o padrão (Cabelo Curto e Sorrindo). Use se a imagem não estiver carregando.")
        if st.button("⚠️ Redefinir Avatar Completamente", type="primary"):
            from utils import get_default_avatar_config
            from database import get_database
            
            with st.spinner("Restaurando configurações de fábrica..."):
                default_config = get_default_avatar_config()
                default_url = get_avatar_url(default_config)
                
                # Force update session
                st.session_state.avatar_config = default_config
                st.session_state.user_profile["avatar_config"] = default_config
                st.session_state.user_profile["avatar"] = default_url
                
                # Force save to DB
                db = get_database()
                email = st.session_state.user_profile.get("email")
                if db.save_avatar_config(email, default_config, default_url):
                    st.success("Avatar redefinido com sucesso!")
                    import time
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Erro ao redefinir no banco de dados.")

st.divider()

# --- Personal Data Section ---
st.header("📝 Dados Pessoais")

# Get current values or defaults
current_profile = st.session_state.user_profile or {}

default_name = current_profile.get("name", "")
default_nickname = current_profile.get("nickname", "")
default_age = current_profile.get("age", 10)
default_confidence = current_profile.get("confidence", 5)
default_interests = current_profile.get("interests", [])
default_school_year = current_profile.get("school_year", "6º ano")
default_school_name = current_profile.get("school_name", "")

# Form Fields
name = st.text_input("Qual é o seu nome?", value=default_name)
nickname = st.text_input("Como você quer ser chamado no Ranking? (Apelido)", value=default_nickname, help="Esse nome aparecerá para os outros alunos. Se deixar em branco, criaremos um nome secreto para você!")
age = st.number_input("Quantos anos você tem?", min_value=5, max_value=100, value=default_age)

school_year = st.selectbox(
    "Em que ano você estuda?",
    ["1º ano", "2º ano", "3º ano", "4º ano", "5º ano", "6º ano", "7º ano", "8º ano", "9º ano", "1º ano EM", "2º ano EM", "3º ano EM"],
    index=["1º ano", "2º ano", "3º ano", "4º ano", "5º ano", "6º ano", "7º ano", "8º ano", "9º ano", "1º ano EM", "2º ano EM", "3º ano EM"].index(default_school_year) if default_school_year in ["1º ano", "2º ano", "3º ano", "4º ano", "5º ano", "6º ano", "7º ano", "8º ano", "9º ano", "1º ano EM", "2º ano EM", "3º ano EM"] else 5
)

school_name = st.text_input("Nome da sua escola:", value=default_school_name)

confidence = st.slider("De 1 a 10, o quanto você gosta de matemática?", 1, 10, default_confidence)

# Predefined options and custom logic
predefined_options = ["Ler histórias", "Jogar videogames", "Resolver quebra-cabeças", "Desenhar", "Esportes", "Música", "Espaço", "Dinossauros", "Culinária"]

# Detect existing custom interests saved in default_interests
custom_interests = [item for item in default_interests if item not in predefined_options]
custom_val = custom_interests[0] if custom_interests else ""

# Build default selections
default_selected = [item for item in default_interests if item in predefined_options]
if custom_interests:
    default_selected.append("Outros")
    
interests = st.multiselect(
    "O que você mais gosta de fazer?",
    predefined_options + ["Outros"],
    default=default_selected
)

# Text input for "Outros" interest
custom_interest_input = ""
if "Outros" in interests:
    custom_interest_input = st.text_input(
        "O que mais você gosta de fazer? Digite aqui:",
        value=custom_val,
        placeholder="Ex: Jogar xadrez, programar, andar de skate, astronomia...",
        help="Este tema será utilizado pelo MatemAI para contextualizar seus problemas de matemática!"
    )
    
# Learning Impact Card (Evidencing the impact on learning)
st.markdown("""
<div class="learning-impact-card">
    <div class="card-header">
        <span class="icon">🧠</span>
        <span class="title">Seus Interesses Adaptam Seu Aprendizado!</span>
    </div>
    <div class="card-body">
        O <b>MatemAI</b> utiliza seus gostos pessoais (incluindo o que você digitar em <b>Outros</b>) 
        para personalizar as missões e exercícios matemáticos. Se você escolher <i>Música</i> ou 
        escrever algo como <i>"Futebol"</i>, a nossa IA vai contextualizar os problemas 
        de matemática com esses temas, tornando tudo muito mais divertido e fácil de aprender!
    </div>
</div>
<style>
.learning-impact-card {
    background: linear-gradient(135deg, rgba(0, 71, 171, 0.04) 0%, rgba(0, 191, 255, 0.04) 100%);
    border: 1px dashed rgba(0, 71, 171, 0.25);
    border-left: 5px solid #0047AB;
    padding: 16px;
    border-radius: 12px;
    margin-top: 15px;
    margin-bottom: 20px;
    box-shadow: 0 4px 15px rgba(0, 71, 171, 0.02);
}
.learning-impact-card .card-header {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 6px;
}
.learning-impact-card .icon {
    font-size: 1.25rem;
}
.learning-impact-card .title {
    font-weight: bold;
    color: #0047AB;
    font-size: 1rem;
}
.learning-impact-card .card-body {
    color: #2C3E50;
    font-size: 0.92rem;
    line-height: 1.6;
}
</style>
""", unsafe_allow_html=True)

submitted = st.button("Salvar Perfil", type="primary", use_container_width=True)

if submitted:
    if not name:
        st.error("Por favor, digite seu nome.")
    else:
        # Process interest list to map "Outros" to user's typed value
        final_interests = [item for item in interests if item != "Outros"]
        if "Outros" in interests and custom_interest_input.strip():
            final_interests.append(custom_interest_input.strip())
            
        # AI Agent Logic
        answers = {
            "name": name,
            "nickname": nickname,
            "age": age,
            "school_year": school_year,
            "school_name": school_name,
            "confidence": confidence,
            "interest": " ".join(final_interests)
        }
        
        # Clear cache if interests changed significantly (optional, but good practice)
        # st.cache_data.clear() 
        
        methodology = get_ai_methodology(answers)
        
        # Update Session State
        st.session_state.user_profile.update({
            "name": name,
            "nickname": nickname,
            "age": age,
            "school_year": school_year,
            "school_name": school_name,
            "confidence": confidence,
            "interests": final_interests,
            "methodology": methodology
        })
        
        # Save progress
        save_user_progress()
        
        st.success(f"Perfil atualizado! Nova metodologia: **{methodology}**")
        st.balloons()
        
        # Mensagem de redirecionamento
        st.info("🚀 Redirecionando para Desafios Gamificados em 5 segundos...")
        
        # Aguardar 5 segundos e redirecionar
        import time
        time.sleep(5)
        st.switch_page("pages/2_Desafios_Gamificados.py")

st.markdown("---")
st.markdown("### 📜 Histórico de Habilidades Desenvolvidas")

if "completed_bncc_skills" in st.session_state and st.session_state.completed_bncc_skills:
    skills_data = []
    # Create a mapping of mission ID to Title if possible, otherwise just use ID
    missions_map = {m['id']: m['title'] for m in st.session_state.missions} if 'missions' in st.session_state else {}
    
    for mission_id, skill_info in st.session_state.completed_bncc_skills.items():
        # Try to find mission title
        mission_title = missions_map.get(mission_id, f"Missão {mission_id}")
        # If mission_id is a string like 'mission_1', try to match
        if isinstance(mission_id, str) and mission_id.startswith('mission_'):
             try:
                 m_id_int = int(mission_id.split('_')[1])
                 mission_title = missions_map.get(m_id_int, mission_title)
             except:
                 pass

        skills_data.append({
            "Habilidade BNCC": skill_info.get("habilidade", "N/A"),
            "Descrição": skill_info.get("habilidade_texto", "N/A"),
            "Missão": mission_title
        })
    
    st.dataframe(skills_data, use_container_width=True, hide_index=True)
else:
    st.info("Nenhuma habilidade registrada ainda. Complete missões para desenvolver habilidades!")
