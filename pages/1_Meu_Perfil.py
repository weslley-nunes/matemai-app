import streamlit as st
from utils import get_ai_methodology, setup_app, show_sidebar

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
