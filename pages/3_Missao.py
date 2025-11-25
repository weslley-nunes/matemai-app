import streamlit as st
from utils import setup_app, get_ai_agent, show_sidebar, complete_mission, save_user_progress, update_problem_solved, update_mission_completed
import time

# Initialize Session State
setup_app()
show_sidebar()

if "current_mission" not in st.session_state or not st.session_state.current_mission:
    st.warning("Nenhuma missão selecionada. Volte para os Desafios!")
    st.page_link("pages/2_Desafios_Gamificados.py", label="Voltar para Desafios", icon="🔙")
    st.stop()

mission = st.session_state.current_mission
agent = get_ai_agent()

st.title(f"⚔️ Missão: {mission['title']}")
st.markdown(f"**Objetivo:** {mission['desc']}")

# Get and display BNCC alignment
school_year = st.session_state.user_profile.get("school_year", "6º ano") if st.session_state.user_profile else "6º ano"

if "bncc_alignment" not in st.session_state or st.session_state.get("bncc_mission_id") != mission['id']:
    with st.spinner("Consultando BNCC..."):
        try:
            bncc_data = agent.get_bncc_alignment(
                mission['title'], 
                mission['desc'], 
                school_year,
                st.session_state.level
            )
            st.session_state.bncc_alignment = bncc_data
            st.session_state.bncc_mission_id = mission['id']
        except Exception as e:
            st.session_state.bncc_alignment = {
                "competencia": "Competência 1",
                "competencia_texto": "Reconhecer que a Matemática é uma ciência humana.",
                "habilidade": "EF06MA01",
                "habilidade_texto": "Comparar e ordenar números naturais."
            }

bncc = st.session_state.bncc_alignment

# Display BNCC info in an attractive box
st.markdown(f"""
<div style="background: linear-gradient(135deg, #1E88E5 0%, #1565C0 100%); padding: 20px; border-radius: 15px; margin: 20px 0; color: white;">
    <div style="font-size: 14px; font-weight: bold; margin-bottom: 10px; opacity: 0.9;">📚 BNCC - Base Nacional Comum Curricular</div>
    <div style="margin-bottom: 15px;">
        <div style="font-weight: bold; font-size: 16px; margin-bottom: 5px;">🎯 {bncc['competencia']}</div>
        <div style="font-size: 14px; opacity: 0.95;">{bncc['competencia_texto']}</div>
    </div>
    <div style="background: rgba(255,255,255,0.2); padding: 12px; border-radius: 10px;">
        <div style="font-weight: bold; font-size: 15px; margin-bottom: 5px;">✅ Habilidade: {bncc['habilidade']}</div>
        <div style="font-size: 14px;">{bncc['habilidade_texto']}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Generate Problem (Cached in Session State to persist across reruns)
if "current_problem" not in st.session_state or st.session_state.current_problem_mission_id != mission['id']:
    with st.spinner("O Mestre dos Desafios está criando um problema para você..."):
        try:
            problem_data = agent.generate_problem(mission['title'], mission['desc'], st.session_state.level)
        except AttributeError:
            st.cache_resource.clear()
            agent = get_ai_agent()
            problem_data = agent.generate_problem(mission['title'], mission['desc'], st.session_state.level)
            
        st.session_state.current_problem = problem_data
        st.session_state.current_problem_mission_id = mission['id']
        st.session_state.problem_solved = False

problem = st.session_state.current_problem

# Display Problem
st.markdown("---")
st.subheader("📝 Seu Desafio:")
st.info(problem['question'])

if st.session_state.problem_solved:
    st.success("✅ Missão Cumprida!")
    st.balloons()
    if st.button("Voltar para o Mapa"):
        st.switch_page("pages/2_Desafios_Gamificados.py")
else:
    # Initialize attempt counter for current problem
    if "problem_attempts" not in st.session_state:
        st.session_state.problem_attempts = {}
    
    problem_key = f"{mission['id']}_{st.session_state.current_problem_mission_id}"
    if problem_key not in st.session_state.problem_attempts:
        st.session_state.problem_attempts[problem_key] = 0
    
    with st.form("answer_form"):
        user_answer = st.text_input("Sua Resposta:")
        submitted = st.form_submit_button("Enviar Resposta")
        
        if submitted:
            if not user_answer:
                st.warning("Por favor, escreva uma resposta.")
            else:

                # Check Battery
                from utils import consume_battery
                
                if not consume_battery():
                    st.error("🔋 Bateria Neural Esgotada!")
                    st.warning("Você precisa de mais energia para continuar aprendendo hoje.")
                    time.sleep(2)
                    st.switch_page("pages/6_Premium.py")
                
                # Increment attempt counter
                st.session_state.problem_attempts[problem_key] += 1
                current_attempt = st.session_state.problem_attempts[problem_key]
                
                with st.spinner("Verificando..."):
                    try:
                        # Try with attempt_number and expected_answer parameters
                        validation = agent.validate_answer(
                            problem['question'], 
                            user_answer,
                            attempt_number=current_attempt,
                            expected_answer=problem.get('solution')
                        )
                    except TypeError:
                        # Fallback: agent might be cached with old signature
                        # Clear cache and try again
                        st.cache_resource.clear()
                        agent = get_ai_agent()
                        validation = agent.validate_answer(
                            problem['question'], 
                            user_answer,
                            attempt_number=current_attempt,
                            expected_answer=problem.get('solution')
                        )
                    except AttributeError:
                        st.cache_resource.clear()
                        agent = get_ai_agent()
                        validation = agent.validate_answer(
                            problem['question'], 
                            user_answer,
                            attempt_number=current_attempt,
                            expected_answer=problem.get('solution')
                        )
                
                if validation['correct']:
                    # Reset attempt counter for this problem
                    st.session_state.problem_attempts[problem_key] = 0
                    
                    # Track problem solved correctly for daily missions
                    update_problem_solved(is_correct=True)
                    
                    st.success(validation['feedback'])
                    
                    # Update Stats
                    st.session_state.exercises_completed_count += 1
                    st.session_state.current_streak += 1
                    
                    # Calculate XP with Streak Bonus
                    earned_xp = mission['xp']
                    
                    # Check/Activate Double XP
                    from utils import activate_double_xp, is_double_xp_active
                    
                    # Activate if streak reached 3 just now
                    if st.session_state.current_streak == 3:
                        activate_double_xp()
                        st.toast("🔥 MODO XP EM DOBRO ATIVADO! (2 min)", icon="🔥")
                    
                    # Apply multiplier if active
                    double_xp_active, _ = is_double_xp_active()
                    if double_xp_active:
                        earned_xp *= 2
                        
                        # Show streak bonus message with animation
                        st.markdown(f"""
                        <div style="
                            padding: 20px; 
                            background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%); 
                            color: #000; 
                            border-radius: 15px; 
                            text-align: center; 
                            margin: 20px 0;
                            box-shadow: 0 8px 20px rgba(255, 215, 0, 0.4);
                            animation: pulse 1.5s ease-in-out;
                        ">
                            <h2 style="margin: 0 0 10px 0; font-size: 28px;">🔥 XP EM DOBRO! 🔥</h2>
                            <p style="margin: 0; font-size: 18px; font-weight: bold;">
                                Aproveite o bônus de tempo limitado!
                            </p>
                            <p style="margin: 10px 0 0 0; font-size: 16px;">
                                +{earned_xp} XP (dobrado de {mission['xp']} XP)
                            </p>
                        </div>
                        <style>
                        @keyframes pulse {{
                            0%, 100% {{ transform: scale(1); }}
                            50% {{ transform: scale(1.05); }}
                        }}
                        </style>
                        """, unsafe_allow_html=True)
                        
                        # Delay before balloons
                        time.sleep(1)
                        st.balloons()
                    
                    st.session_state.xp += earned_xp
                    
                    # Level Up Logic
                    if st.session_state.exercises_completed_count % 4 == 0:
                        st.session_state.level += 1
                        st.markdown(f"""
                        <div style="padding: 20px; background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%); color: white; border-radius: 15px; text-align: center; margin: 20px 0; box-shadow: 0 8px 20px rgba(76, 175, 80, 0.4);">
                            <h2 style="margin: 0 0 10px 0;">🆙 SUBIU DE NÍVEL!</h2>
                            <p style="margin: 0; font-size: 20px; font-weight: bold;">Você alcançou o Nível {st.session_state.level}!</p>
                        </div>
                        """, unsafe_allow_html=True)
                        time.sleep(1)
                        st.balloons()

                    st.session_state.problem_solved = True
                    
                    # Complete Mission and Unlock Next
                    complete_mission(mission['id'])
                    
                    # Save BNCC data for this completed mission
                    if "completed_bncc_skills" not in st.session_state:
                        st.session_state.completed_bncc_skills = {}
                    
                    if "bncc_alignment" in st.session_state:
                        st.session_state.completed_bncc_skills[mission['id']] = st.session_state.bncc_alignment
                    
                    # Track mission completion for daily missions
                    update_mission_completed()
                    
                    # Salvar progresso no Firestore
                    save_user_progress()
                    
                    st.rerun()
                else:
                    # Track problem solved incorrectly for daily missions
                    update_problem_solved(is_correct=False)
                    
                    st.session_state.current_streak = 0 # Reset streak on wrong answer
                    st.error(validation['feedback'])
                    st.warning(f"💡 Dica: {problem['hint']}")
