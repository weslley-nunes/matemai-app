import streamlit as st
from utils import get_missions, setup_app, show_sidebar
import os
import html
import base64

setup_app()
show_sidebar()

st.title("🗺️ Desafios Gamificados")

if not st.session_state.user_profile:
    st.warning("Por favor, crie seu perfil primeiro!")
    st.stop()

methodology = st.session_state.user_profile["methodology"]
missions = get_missions(methodology, st.session_state.level)

if not missions:
    st.warning("Nenhuma missão disponível.")
    st.stop()

# BNCC Skills Tracker at the top
st.markdown("### 📚 Habilidades BNCC Desenvolvidas")

# Initialize BNCC tracking if not exists
if "completed_bncc_skills" not in st.session_state:
    st.session_state.completed_bncc_skills = {}

# Get completed missions
completed_missions = [m for m in missions if m["status"] == "completed"]

if completed_missions:
    # Display completed skills in a horizontal scrollable container
    st.markdown("""
    <div style="background: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); margin-bottom: 30px;">
        <div style="display: flex; gap: 15px; overflow-x: auto; padding-bottom: 10px;">
    """, unsafe_allow_html=True)
    
    for mission in completed_missions:
        mission_id = mission['id']
        
        # Check if we have BNCC data for this mission
        if mission_id in st.session_state.completed_bncc_skills:
            bncc = st.session_state.completed_bncc_skills[mission_id]
            
            st.markdown(f"""
            <div style="min-width: 280px; background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%); padding: 15px; border-radius: 12px; border-left: 5px solid #1976D2; flex-shrink: 0;">
                <div style="font-weight: bold; color: #1565C0; font-size: 15px; margin-bottom: 8px;">
                    ✅ {bncc.get('habilidade', 'N/A')}
                </div>
                <div style="font-size: 13px; color: #424242; line-height: 1.4;">
                    {bncc.get('habilidade_texto', 'Habilidade desenvolvida')[:100]}...
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Summary
    total_skills = len(st.session_state.completed_bncc_skills)
    st.markdown(f"""
        <div style="text-align: center; margin-top: 15px; padding: 12px; background: linear-gradient(135deg, #1E88E5 0%, #1565C0 100%); color: white; border-radius: 10px; font-weight: bold; font-size: 16px;">
            🎓 {total_skills} Habilidade{'s' if total_skills != 1 else ''} Desenvolvida{'s' if total_skills != 1 else ''}
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div style="background: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); margin-bottom: 30px; text-align: center;">
        <div style="color: #666; font-size: 15px;">
            🎓 Complete missões para desenvolver habilidades da BNCC!
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Função para converter imagem para base64
def get_img_as_base64(file_path):
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        return f"data:image/png;base64,{base64.b64encode(data).decode()}"
    except Exception:
        return None

# CSS inline para trilha estilo Duolingo
st.markdown("""
<style>
.trail-container {
    max-width: 600px;
    margin: 40px auto;
    position: relative;
    padding: 20px;
}
/* LINHA VERTICAL DE FUNDO */
.trail-line {
    position: absolute;
    left: 50%;
    top: 20px;
    bottom: 20px;
    width: 8px;
    background: linear-gradient(to bottom, #0047AB, #00BFFF);
    transform: translateX(-50%);
    z-index: 0;
    border-radius: 4px;
}
.mission-row {
    display: flex;
    justify-content: center;
    align-items: center;
    margin: 60px 0;
    position: relative;
    z-index: 1;
}
.mission-icon-wrapper {
    position: relative;
    cursor: pointer;
    transition: transform 0.2s;
    background: white;
    border-radius: 50%;
    padding: 5px;
}
.mission-icon-wrapper:hover {
    transform: scale(1.1);
}
.mission-icon {
    width: 100px;
    height: 100px;
    border-radius: 50%;
    border: 5px solid;
    box-shadow: 0 6px 20px rgba(0,0,0,0.3);
    object-fit: cover;
    background: white;
    display: block;
}
.icon-locked { border-color: #58595B; filter: grayscale(100%) brightness(0.6); }
.icon-unlocked { border-color: #0047AB; animation: glow 2s infinite; }
.icon-completed { border-color: #FFC800; opacity: 0.8; }

@keyframes glow {
    0%, 100% { box-shadow: 0 6px 20px rgba(0, 71, 171, 0.4); }
    50% { box-shadow: 0 6px 30px rgba(0, 71, 171, 0.8); }
}

.check-badge {
    position: absolute;
    top: 0;
    right: 0;
    width: 35px;
    height: 35px;
    background: #0047AB;
    border-radius: 50%;
    border: 3px solid white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
    color: white;
    font-weight: bold;
    z-index: 2;
}

.tooltip-balloon {
    position: absolute;
    left: 130px;
    top: 50%;
    transform: translateY(-50%);
    background: white;
    padding: 20px;
    border-radius: 15px;
    box-shadow: 0 8px 30px rgba(0,0,0,0.25);
    min-width: 300px;
    opacity: 0;
    visibility: hidden;
    transition: all 0.3s ease;
    z-index: 100;
    pointer-events: none;
}
.mission-icon-wrapper:hover .tooltip-balloon {
    opacity: 1;
    visibility: visible;
}
.tooltip-balloon::before {
    content: '';
    position: absolute;
    left: -10px;
    top: 50%;
    transform: translateY(-50%);
    border-top: 10px solid transparent;
    border-bottom: 10px solid transparent;
    border-right: 10px solid white;
}

/* CAIXA DESTACADA */
.pending-challenge-box {
    background: #E0F7FA;
    border: 2px solid #0047AB;
    border-radius: 20px;
    padding: 25px;
    margin: 30px auto;
    max-width: 500px;
    box-shadow: 0 8px 30px rgba(0, 71, 171, 0.3);
    color: #333;
    text-align: center;
    position: relative;
    z-index: 5;
}
.pending-title {
    font-size: 22px;
    font-weight: bold;
    margin-bottom: 10px;
    color: #0047AB;
}
.pending-desc {
    font-size: 16px;
    margin-bottom: 15px;
    line-height: 1.5;
    opacity: 0.95;
    color: #555;
}
.pending-xp {
    background: #0047AB;
    color: white;
    padding: 8px 20px;
    border-radius: 20px;
    font-weight: bold;
    display: inline-block;
}
</style>
""", unsafe_allow_html=True)

# Layout: Trilha (Esquerda/Centro) + Estatísticas (Direita)
col_trail, col_stats = st.columns([3, 1])

with col_trail:
    # Container da trilha
    st.markdown('<div class="trail-container"><div class="trail-line"></div>', unsafe_allow_html=True)
    
    # Renderizar trilha
    for i, m in enumerate(missions):
        status = m["status"]
        
        # Se for a missão atual (unlocked), não renderizar na trilha, mas sim em destaque abaixo
        if status == "unlocked":
            continue
            
        # Usar sempre a estrela como base, mas mudar para verde se completada
        if status == "completed":
            icon_path = "assets/icons/estrela_azul.png"
        else:
            icon_path = "assets/icons/estrela.png"
            
        icon_b64 = get_img_as_base64(icon_path)
        
        if icon_b64:
            icon_src = icon_b64
        else:
            color = '58595B' if status == 'locked' else '0047AB' if status == 'unlocked' else 'FFC800'
            icon_src = f"https://via.placeholder.com/100/{color}/FFFFFF?text={m['id']}"
        
        icon_class = f"icon-{status}"
        check_html = '<div class="check-badge">✓</div>' if status == "completed" else ''
        
        title = html.escape(m['title'])
        desc = html.escape(m.get('desc', ''))
        
        st.markdown(f'''
        <div class="mission-row">
            <div class="mission-icon-wrapper">
                <img src="{icon_src}" class="mission-icon {icon_class}" />
                {check_html}
                <div class="tooltip-balloon">
                    <div style="font-weight:bold; font-size:18px; margin-bottom:5px; color:#333;">{title}</div>
                    <div style="font-size:14px; color:#666; margin-bottom:10px;">{desc}</div>
                </div>
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
        if status == "completed":
            # Centralizar botão
            c_btn1, c_btn2, c_btn3 = st.columns([1, 2, 1])
            with c_btn2:
                st.button(f"✅ Completada", key=f"btn_{m['id']}", disabled=True, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # SEÇÃO DE DESTAQUE PARA A PRÓXIMA MISSÃO
    # Encontrar a missão desbloqueada
    current_mission = next((m for m in missions if m["status"] == "unlocked"), None)
    
    if current_mission:
        st.markdown("---")
        st.markdown("<h2 style='text-align: center; color: #0047AB;'>🚀 Próximo Desafio</h2>", unsafe_allow_html=True)
        
        # Layout de destaque
        with st.container():
            # Ícone grande
            icon_path = "assets/icons/estrela.png"
            icon_b64 = get_img_as_base64(icon_path)
            
            st.markdown(f"""
            <div style="display: flex; justify-content: center; margin-bottom: 20px;">
                <div class="mission-icon-wrapper" style="transform: scale(1.2);">
                    <img src="{icon_b64}" class="mission-icon icon-unlocked" />
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Caixa de detalhes
            title = html.escape(current_mission['title'])
            desc = html.escape(current_mission.get('desc', ''))
            
            st.markdown(f'''
            <div class="pending-challenge-box">
                <div class="pending-title">🎯 {title}</div>
                <div class="pending-desc">{desc}</div>
                <div class="pending-xp">+{current_mission["xp"]} XP</div>
            </div>
            ''', unsafe_allow_html=True)
            
            # Botão de ação grande
            c_start1, c_start2, c_start3 = st.columns([1, 2, 1])
            with c_start2:
                if st.button(f"🎯 INICIAR MISSÃO AGORA", key=f"btn_start_{current_mission['id']}", use_container_width=True, type="primary"):
                    st.session_state.current_mission = current_mission
                    st.switch_page("pages/3_Missao.py")

with col_stats:
    st.markdown("### 📊 Estatísticas")
    
    # Card de Estatísticas
    st.markdown("""
    <div style="background: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); margin-bottom: 20px;">
    """, unsafe_allow_html=True)
    
    st.metric("🏆 XP Total", st.session_state.xp)
    st.metric("🔥 Nível", st.session_state.level)
    
    completed_count = len([m for m in missions if m["status"] == "completed"])
    st.metric("🎯 Missões", f"{completed_count}/{len(missions)}")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Mascote e Metodologia
    st.markdown(f'<div style="text-align:center; margin-bottom:20px; background: rgba(0, 71, 171, 0.1); color: #0047AB; padding: 10px 20px; border-radius: 25px; border: 2px solid #0047AB;">📚 {methodology}</div>', unsafe_allow_html=True)
    
    if os.path.exists("assets/mascot_wizard.png"):
        st.image("assets/mascot_wizard.png", use_container_width=True)
    elif os.path.exists("assets/mascot.png"):
        st.image("assets/mascot.png", use_container_width=True)
