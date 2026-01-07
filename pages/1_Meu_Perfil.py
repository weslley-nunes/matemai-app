import streamlit as st
from utils import get_ai_methodology, setup_app, show_sidebar
from avatar_assets import AVATAR_ASSETS, get_avatar_url
from database import get_database

# Initialize Session State
setup_app()
show_sidebar()

st.title("👤 Meu Perfil")

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
    
    # DEBUG: Show URL and Config to verify deployment and values
    st.caption(f"Debug Info (v2.0):")
    st.code(avatar_url, language="text")
    # st.json(st.session_state.avatar_config)

    # Display Avatar
    st.image(avatar_url, width=250)
    
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

st.divider()

# --- Personal Data Section ---
st.header("📝 Dados Pessoais")

with st.form("profile_form"):
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
    
    interests = st.multiselect(
        "O que você mais gosta de fazer?",
        ["Ler histórias", "Jogar videogames", "Resolver quebra-cabeças", "Desenhar", "Esportes", "Música", "Espaço", "Dinossauros", "Culinária"],
        default=default_interests
    )
    
    submitted = st.form_submit_button("Salvar Perfil")

    if submitted:
        if not name:
            st.error("Por favor, digite seu nome.")
        else:
            # AI Agent Logic
            answers = {
                "name": name,
                "nickname": nickname,
                "age": age,
                "school_year": school_year,
                "school_name": school_name,
                "confidence": confidence,
                "interest": " ".join(interests)
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
                "interests": interests,
                "methodology": methodology
            })
            
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
