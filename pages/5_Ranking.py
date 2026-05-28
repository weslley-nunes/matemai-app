import streamlit as st
import pandas as pd
import altair as alt
from database import get_database
from utils import setup_app, show_sidebar, generate_nickname, render_avatar

# Setup
setup_app()
show_sidebar()

# Page Title
st.title("🏆 Ranking dos Campeões")
st.markdown("### Quem são os mestres da matemática? 🚀")
st.markdown("Confira o desempenho dos alunos e veja quem está liderando a jornada do conhecimento!")

# Get Data
db = get_database()
leaderboard = db.get_leaderboard(limit=20)

# Get Current User ID
current_user_email = st.session_state.user_profile['email'] if st.session_state.user_profile else None

# Process Leaderboard for Display (Privacy Masking)
display_leaderboard = []
for user in leaderboard:
    user_display = user.copy()
    # If it's NOT the current user, mask the name
    if current_user_email and user.get('id') != current_user_email:
        # Use chosen nickname if available, else generate one
        user_display['name'] = user.get('nickname') or generate_nickname(user.get('id', 'unknown'))
    else:
        # It IS the current user. Show their chosen nickname if they have one, otherwise their real name.
        # Actually, user might want to see what others see? 
        # Requirement: "só o proprio usuário na aba ranking veja o seu próprio nome"
        # But also "crie um campo no cadastro em que ele possa escolher como ele deseja ser chamado"
        # So if they chose a nickname, they probably want to see that.
        # Let's show: Nickname (Real Name) or just Real Name if no nickname.
        if user.get('nickname'):
             user_display['name'] = f"{user['nickname']} ({user['name']})"
        else:
             user_display['name'] = user['name']

    display_leaderboard.append(user_display)

leaderboard = display_leaderboard

if not leaderboard:
    st.info("🌟 O ranking está sendo formado! Seja o primeiro a pontuar completando missões.")
else:
    # --- Top 3 Podium (Creative Visual) ---
    if len(leaderboard) >= 3:
        col1, col2, col3 = st.columns([1, 1, 1])
        
        # 2nd Place
        with col1:
            st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
            st.markdown("🥈 **2º Lugar**")
            if leaderboard[1]['avatar']:
                render_avatar(leaderboard[1]['avatar'], width=80)
            st.markdown(f"**{leaderboard[1]['name']}**")
            st.markdown(f"*{leaderboard[1]['xp']} XP*")
            st.markdown("</div>", unsafe_allow_html=True)
            
        # 1st Place (Center, Larger)
        with col2:
            st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
            st.markdown("🥇 **CAMPEÃO**")
            if leaderboard[0]['avatar']:
                render_avatar(leaderboard[0]['avatar'], width=100)
            st.markdown(f"### {leaderboard[0]['name']}")
            st.markdown(f"**{leaderboard[0]['xp']} XP**")
            st.markdown("</div>", unsafe_allow_html=True)
            
        # 3rd Place
        with col3:
            st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
            st.markdown("🥉 **3º Lugar**")
            if leaderboard[2]['avatar']:
                render_avatar(leaderboard[2]['avatar'], width=80)
            st.markdown(f"**{leaderboard[2]['name']}**")
            st.markdown(f"*{leaderboard[2]['xp']} XP*")
            st.markdown("</div>", unsafe_allow_html=True)
    
    st.divider()

    # --- Performance Charts ---
    st.subheader("📊 Gráfico de Desempenho")
    
    df = pd.DataFrame(leaderboard)
    
    # Bar Chart: XP by Student
    chart = alt.Chart(df).mark_bar(cornerRadiusTopLeft=10, cornerRadiusTopRight=10).encode(
        x=alt.X('name', sort='-y', title='Aluno', axis=alt.Axis(labelAngle=-45)),
        y=alt.Y('xp', title='XP Total'),
        color=alt.Color('xp', scale=alt.Scale(scheme='goldorange'), legend=None),
        tooltip=['name', 'school', 'xp', 'level']
    ).properties(
        height=400,
        title="Top Alunos por XP"
    ).configure_axis(
        grid=False
    ).configure_view(
        strokeWidth=0
    )
    
    st.altair_chart(chart, use_container_width=True)

    # --- Detailed Table ---
    st.subheader("📋 Classificação Geral")
    
    # Custom Table Header
    h_col1, h_col2, h_col3, h_col4, h_col5 = st.columns([0.5, 0.8, 2, 2, 1])
    h_col1.markdown("**#**")
    h_col2.markdown("**Foto**")
    h_col3.markdown("**Nome**")
    h_col4.markdown("**Escola**")
    h_col5.markdown("**XP**")
    st.markdown("---")
    
    # Table Rows
    for i, user in enumerate(leaderboard):
        # Row Layout
        r_col1, r_col2, r_col3, r_col4, r_col5 = st.columns([0.5, 0.8, 2, 2, 1])
        
        # Position
        pos = i + 1
        if pos == 1:
            r_col1.markdown("🥇")
        elif pos == 2:
            r_col1.markdown("🥈")
        elif pos == 3:
            r_col1.markdown("🥉")
        else:
            r_col1.markdown(f"**{pos}º**")
            
        # Avatar
        with r_col2:
            if user['avatar']:
                # Use a small width for table avatar
                render_avatar(user['avatar'], width=40, centered=False)
            else:
                st.write("👤")
        
        # Name & Level
        r_col3.markdown(f"**{user['name']}**")
        
        # School
        r_col4.markdown(f"{user['school']}")
        
        # XP
        r_col5.markdown(f"**{user['xp']}**")
        
        # Divider between rows
        st.markdown("<hr style='margin: 5px 0; opacity: 0.2;'>", unsafe_allow_html=True)
