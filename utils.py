import streamlit as st
from ai_agent import MathAI
from auth import logout
from database import get_database
import os
import base64

# Initialize AI Agent
@st.cache_resource
def get_ai_agent():
    return MathAI()

def get_img_as_base64(file_path):
    """
    Reads an image file and converts it to a base64 string.
    """
    if not os.path.exists(file_path):
        return None
    with open(file_path, "rb") as f:
        data = f.read()
    return f"data:image/png;base64,{base64.b64encode(data).decode()}"

def get_ai_methodology(answers):
    """
    Determines the teaching methodology based on user answers using Gemini AI.
    """
    agent = get_ai_agent()
    
    with st.spinner("O Agente de IA está analisando seu perfil..."):
        result = agent.generate_methodology(answers)
        
    return result.get("methodology", "Standard")

def track_daily_mission_progress():
    """
    Atualiza o progresso das missões diárias baseado nas ações do aluno.
    """
    from datetime import datetime
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    # Initialize daily mission tracking if not exists
    if "daily_mission_progress" not in st.session_state:
        st.session_state.daily_mission_progress = {}
    
    if today_str not in st.session_state.daily_mission_progress:
        st.session_state.daily_mission_progress[today_str] = {
            "study_time_minutes": 0,
            "missions_completed": 0,
            "problems_solved": 0,
            "consecutive_correct": 0,
            "max_consecutive_correct": 0,
            "last_answer_correct": False
        }
    
    return st.session_state.daily_mission_progress[today_str]

def update_mission_study_time(minutes):
    """
    Adiciona tempo de estudo ao progresso diário.
    """
    progress = track_daily_mission_progress()
    progress["study_time_minutes"] += minutes
    
    # Update Daily Streak
    update_daily_streak()

def update_daily_streak():
    """
    Atualiza a ofensiva diária (dias seguidos estudando).
    """
    from datetime import datetime, timedelta
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    if "last_study_date" not in st.session_state:
        st.session_state.last_study_date = ""
        
    last_date = st.session_state.last_study_date
    
    # Se já estudou hoje, não faz nada
    if last_date == today_str:
        return

    # Se nunca estudou, ou estudou antes de ontem (quebrou a sequência)
    if not last_date:
        st.session_state.current_study_streak = 1
    else:
        try:
            last_dt = datetime.strptime(last_date, "%Y-%m-%d")
            today_dt = datetime.strptime(today_str, "%Y-%m-%d")
            diff = (today_dt - last_dt).days
            
            if diff == 1:
                # Estudou ontem, incrementa
                st.session_state.current_study_streak += 1
            elif diff > 1:
                # Quebrou a sequência, reinicia
                st.session_state.current_study_streak = 1
            # Se diff < 1 (futuro?), ignora
        except ValueError:
            st.session_state.current_study_streak = 1
            
    # Atualiza data e salva
    st.session_state.last_study_date = today_str
    if st.session_state.get("logged_in"):
        save_user_progress()

def update_mission_completed():
    """
    Incrementa o contador de missões completadas.
    """
    progress = track_daily_mission_progress()
    progress["missions_completed"] += 1

def update_problem_solved(is_correct):
    """
    Atualiza contadores de problemas resolvidos e sequência de acertos.
    """
    progress = track_daily_mission_progress()
    progress["problems_solved"] += 1
    
    if is_correct:
        if progress["last_answer_correct"]:
            progress["consecutive_correct"] += 1
        else:
            progress["consecutive_correct"] = 1
        progress["last_answer_correct"] = True
        
        # Update max consecutive
        if progress["consecutive_correct"] > progress["max_consecutive_correct"]:
            progress["max_consecutive_correct"] = progress["consecutive_correct"]
    else:
        progress["consecutive_correct"] = 0
        progress["last_answer_correct"] = False
        
    # Update Daily Streak
    update_daily_streak()

def check_mission_eligibility(mission_id):
    """
    Verifica se o aluno cumpriu os requisitos para resgatar uma missão.
    """
    progress = track_daily_mission_progress()
    
    mission_requirements = {
        "mission_1": progress["study_time_minutes"] >= 15,
        "mission_2": progress["missions_completed"] >= 1,
        "mission_3": progress["problems_solved"] >= 3,
        "mission_4": progress["max_consecutive_correct"] >= 5,
    }
    
    return mission_requirements.get(mission_id, False)

def get_missions(methodology, level):
    """
    Returns the list of missions, generating initial ones if needed.
    """
    # Initialize missions in session state if not present or empty
    if "missions" not in st.session_state or not st.session_state.missions:
        agent = get_ai_agent()
        interests = st.session_state.user_profile.get("interests", [])
        interests_str = ", ".join(interests) if interests else "General Math"
        
        # Get completed BNCC skills for context
        completed_skills = st.session_state.get("completed_bncc_skills", {})
        
        with st.spinner("Gerando sua trilha de aprendizado..."):
            try:
                initial_missions = agent.generate_missions(
                    methodology, 
                    level, 
                    interests_str,
                    completed_bncc_skills=completed_skills
                )
            except AttributeError:
                st.cache_resource.clear()
                agent = get_ai_agent()
                initial_missions = agent.generate_missions(
                    methodology, 
                    level, 
                    interests_str,
                    completed_bncc_skills=completed_skills
                )
            except Exception as e:
                print(f"Warning: Error generating missions: {e}")
                # Return fallback missions
                initial_missions = [
                    {
                        "id": 1,
                        "title": "Primeira Aventura Matemática",
                        "desc": "Comece sua jornada resolvendo problemas básicos!",
                        "xp": 100,
                        "status": "unlocked"
                    },
                    {
                        "id": 2,
                        "title": "Desafio Intermediário",
                        "desc": "Continue avançando!",
                        "xp": 150,
                        "status": "locked"
                    },
                    {
                        "id": 3,
                        "title": "Missão Avançada",
                        "desc": "Teste suas habilidades!",
                        "xp": 200,
                        "status": "locked"
                    }
                ]
                
            # Validate and assign IDs
            if not initial_missions or len(initial_missions) == 0:
                # Fallback silently or with a log if needed, but avoid scary errors for the user
                print("Warning: No missions generated by AI. Using default missions.")
                initial_missions = [
                    {
                        "id": 1,
                        "title": "Primeira Aventura Matemática",
                        "desc": "Comece sua jornada resolvendo problemas básicos!",
                        "xp": 100,
                        "status": "unlocked"
                    }
                ]
            
            # Assign IDs if not present
            for i, m in enumerate(initial_missions):
                if "id" not in m:
                    m["id"] = i + 1
                    
            st.session_state.missions = initial_missions

    return st.session_state.missions

def complete_mission(mission_id):
    """
    Marks a mission as complete, unlocks the next one, and generates a new one if needed.
    """
    # Find the mission
    mission_index = -1
    for i, m in enumerate(st.session_state.missions):
        if m["id"] == mission_id:
            mission_index = i
            break
    
    if mission_index == -1:
        return

    # Mark as complete (visual change only, logic uses unlocked status of next)
    st.session_state.missions[mission_index]["status"] = "completed"
    
    # Unlock next mission
    next_index = mission_index + 1
    if next_index < len(st.session_state.missions):
        st.session_state.missions[next_index]["status"] = "unlocked"
    else:
        # Generate a NEW mission to extend the track
        agent = get_ai_agent()
        last_mission = st.session_state.missions[mission_index]
        interests = st.session_state.user_profile.get("interests", [])
        interests_str = ", ".join(interests) if interests else "General Math"
        
        with st.spinner("Desbloqueando nova fase..."):
            try:
                new_mission = agent.generate_next_mission(
                    last_mission["title"], 
                    st.session_state.user_profile["methodology"], 
                    st.session_state.level, 
                    interests_str
                )
            except AttributeError:
                st.cache_resource.clear()
                agent = get_ai_agent()
                new_mission = agent.generate_next_mission(
                    last_mission["title"], 
                    st.session_state.user_profile["methodology"], 
                    st.session_state.level, 
                    interests_str
                )
            
            new_mission["id"] = len(st.session_state.missions) + 1
            new_mission["status"] = "unlocked"
            st.session_state.missions.append(new_mission)

def save_user_progress():
    """
    Salva o progresso atual no Firestore
    """
    if st.session_state.user_profile:
        email = st.session_state.user_profile.get('email')
        if email:
            db = get_database()
            db.save_progress(
                email=email,
                xp=st.session_state.xp,
                level=st.session_state.level,
                profile_data=st.session_state.user_profile,
                missions_data=st.session_state.get('missions', []),
                exercises_completed_count=st.session_state.get('exercises_completed_count', 0),
                current_streak=st.session_state.get('current_streak', 0),
                # Study Schedule Data
                study_days=st.session_state.get('study_days', {}),
                current_study_streak=st.session_state.get('current_study_streak', 0),
                # Daily Missions Data
                daily_missions=st.session_state.get('daily_missions', {}),
                daily_missions_xp=st.session_state.get('daily_missions_xp', {}),
                daily_mission_progress=st.session_state.get('daily_mission_progress', {}),
                # BNCC Skills Data
                completed_bncc_skills=st.session_state.get('completed_bncc_skills', {}),
                # Neural Battery
                neural_battery=st.session_state.get('neural_battery', 10),
                last_battery_reset=st.session_state.get('last_battery_reset', ""),
                # Streak Data
                last_study_date=st.session_state.get('last_study_date', "")
            )

def load_user_progress(email):
    """
    Carrega o progresso do Firestore
    """
    db = get_database()
    progress = db.load_progress(email)
    
    if progress:
        st.session_state.xp = progress['xp']
        st.session_state.level = progress['level']
        st.session_state.user_profile.update(progress['profile'])
        st.session_state.missions = progress['missions']
        st.session_state.exercises_completed_count = progress.get('exercises_completed_count', 0)
        st.session_state.current_streak = progress.get('current_streak', 0)
        # Study Schedule Data
        st.session_state.study_days = progress.get('study_days', {})
        st.session_state.current_study_streak = progress.get('current_study_streak', 0)
        # Daily Missions Data
        st.session_state.daily_missions = progress.get('daily_missions', {})
        st.session_state.daily_missions_xp = progress.get('daily_missions_xp', {})
        st.session_state.daily_mission_progress = progress.get('daily_mission_progress', {})
        # BNCC Skills Data
        st.session_state.completed_bncc_skills = progress.get('completed_bncc_skills', {})
        # Neural Battery
        st.session_state.neural_battery = progress.get('neural_battery', 10)
        st.session_state.last_battery_reset = progress.get('last_battery_reset', "")
        # Streak Data
        st.session_state.last_study_date = progress.get('last_study_date', "")
        return True
    return False

def init_session_state():
    if "user_profile" not in st.session_state:
        st.session_state.user_profile = None
    if "xp" not in st.session_state:
        st.session_state.xp = 0
    if "level" not in st.session_state:
        st.session_state.level = 1
    if "exercises_completed_count" not in st.session_state:
        st.session_state.exercises_completed_count = 0
    if "current_streak" not in st.session_state:
        st.session_state.current_streak = 0
    
    # Initialize Neural Battery
    if "neural_battery" not in st.session_state:
        st.session_state.neural_battery = 10
    if "last_battery_reset" not in st.session_state:
        from datetime import datetime
        st.session_state.last_battery_reset = datetime.now().strftime("%Y-%m-%d")
    
    # Check for daily reset
    check_daily_battery_reset()

def check_daily_battery_reset():
    """Reseta a bateria se for um novo dia"""
    from datetime import datetime
    today = datetime.now().strftime("%Y-%m-%d")
    
    if st.session_state.last_battery_reset != today:
        st.session_state.neural_battery = 10
        st.session_state.last_battery_reset = today
        # Salvar o reset no banco se estiver logado
        if st.session_state.get("logged_in"):
            save_user_progress()

def consume_battery():
    """Consome 1 carga da bateria. Retorna True se sucesso, False se sem bateria."""
    # Premium users have unlimited battery
    if st.session_state.user_profile and st.session_state.user_profile.get("is_premium"):
        return True
        
    check_daily_battery_reset()
    
    if st.session_state.neural_battery > 0:
        st.session_state.neural_battery -= 1
        return True
    return False

def get_battery_status():
    """Retorna (atual, maximo)"""
    if st.session_state.user_profile and st.session_state.user_profile.get("is_premium"):
        return 999, 999 # Infinite symbol representation logic can be handled in UI
    return st.session_state.neural_battery, 10

def setup_app():
    """
    Configuração global da aplicação.
    Deve ser chamada no início de todas as páginas.
    """
    # Load Custom CSS
    css_file = "assets/style.css"
    if os.path.exists(css_file):
        with open(css_file, encoding='utf-8') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    
    # Renderizar Logo no topo superior esquerdo (todas as páginas)
    if os.path.exists("assets/logo_matemai.png"):
        st.logo("assets/logo_matemai.png")
    
    # Inicializar Sessão
    init_session_state()

def reset_current_user_progress():
    if st.session_state.user_profile:
        email = st.session_state.user_profile.get('email')
        if email:
            db = get_database()
            if db.reset_progress(email):
                # Reset session state
                st.session_state.xp = 0
                st.session_state.level = 1
                st.session_state.missions = []
                st.session_state.exercises_completed_count = 0
                st.session_state.current_streak = 0
                st.success("Progresso resetado com sucesso!")
                st.success("Progresso resetado com sucesso!")
                st.rerun()

def activate_double_xp():
    """Ativa o modo XP em dobro por 2 minutos"""
    import time
    st.session_state.double_xp_end_time = time.time() + 120 # 2 minutos

def is_double_xp_active():
    """Verifica se o modo XP em dobro está ativo. Retorna (bool, remaining_seconds)"""
    import time
    if "double_xp_end_time" not in st.session_state:
        return False, 0
    
    remaining = st.session_state.double_xp_end_time - time.time()
    if remaining > 0:
        return True, remaining
    return False, 0

def show_sidebar():
    """
    Displays the consistent sidebar with user info.
    """

    with st.sidebar:
        avatar_url = None
        if st.session_state.user_profile and st.session_state.user_profile.get("avatar"):
            avatar_url = st.session_state.user_profile["avatar"]
        elif os.path.exists("assets/mascot.png"):
            avatar_url = get_img_as_base64("assets/mascot.png")
            
        if avatar_url:
            st.markdown(f"""
            <div class="profile-photo-frame">
                <img src="{avatar_url}" width="100">
            </div>
            """, unsafe_allow_html=True)
        
        # Show Double XP indicator if active
        double_xp_active, remaining_seconds = is_double_xp_active()
        
        if double_xp_active:
            minutes = int(remaining_seconds // 60)
            seconds = int(remaining_seconds % 60)
            
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
                padding: 10px;
                border-radius: 10px;
                text-align: center;
                margin: 10px 0;
                box-shadow: 0 4px 15px rgba(255, 215, 0, 0.5);
                animation: glow 2s ease-in-out infinite;
            ">
                <div style="font-weight: bold; font-size: 16px; color: #000;">
                    🔥 XP EM DOBRO 🔥
                </div>
                <div style="font-size: 20px; font-weight: bold; color: #D32F2F; margin-top: 5px;">
                    {minutes:02d}:{seconds:02d}
                </div>
                <div style="font-size: 12px; color: #333; margin-top: 5px;">
                    Aproveite!
                </div>
            </div>
            <style>
            @keyframes glow {{
                0%, 100% {{ 
                    box-shadow: 0 4px 15px rgba(255, 215, 0, 0.5);
                    transform: scale(1);
                }}
                50% {{ 
                    box-shadow: 0 6px 25px rgba(255, 215, 0, 0.8);
                    transform: scale(1.02);
                }}
            }}
            </style>
            """, unsafe_allow_html=True)
            
            # Auto-rerun to update timer
            import time
            time.sleep(1)
            st.rerun()
        
        if st.session_state.user_profile:
            st.write(f"👋 Olá, **{st.session_state.user_profile['name']}**!")
            st.write(f"🏆 XP: {st.session_state.xp}")
            st.write(f"📚 Nível: {st.session_state.level}")
            
            # Battery Display
            battery, max_battery = get_battery_status()
            battery_pct = (battery / max_battery) * 100
            battery_color = "#4CAF50" if battery > 3 else "#F44336"
            
            st.markdown(f"""
            <div style="margin-top: 10px; margin-bottom: 20px;">
                <div style="display: flex; justify-content: space-between; font-size: 14px; margin-bottom: 5px;">
                    <span>🔋 Bateria Neural</span>
                    <span style="font-weight: bold; color: {battery_color}">{battery}/{max_battery}</span>
                </div>
                <div style="width: 100%; background-color: #e0e0e0; border-radius: 10px; height: 10px;">
                    <div style="width: {battery_pct}%; background-color: {battery_color}; height: 10px; border-radius: 10px; transition: width 0.5s;"></div>
                </div>
                <div style="font-size: 11px; color: #666; margin-top: 3px;">
                    Reseta diariamente. Use com sabedoria!
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.page_link("pages/5_Ranking.py", label="Ver Ranking", icon="🏆")
            
            st.markdown("---")
            
            col_logout, col_reset = st.columns(2)
            
            with col_logout:
                if st.button("Sair", key="sidebar_logout"):
                    logout()
            
            with col_reset:
                if st.button("ZERAR", key="sidebar_reset", help="Apagar todo o progresso"):
                    show_reset_confirmation()
        else:
            st.info("Faça login para ver seu progresso.")

    # Alerta Central (fora da sidebar)
@st.dialog("⚠️ ATENÇÃO!")
def show_reset_confirmation():
    st.write("Você está prestes a **APAGAR TODO O SEU PROGRESSO**.")
    st.write("Isso inclui XP, Nível e Missões completadas.")
    st.error("**Essa ação não pode ser desfeita!**")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ SIM, ZERAR", type="primary", use_container_width=True):
            reset_current_user_progress()
            st.rerun()
    with col2:
        if st.button("❌ CANCELAR", use_container_width=True):
            st.rerun()

