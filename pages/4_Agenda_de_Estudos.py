import streamlit as st
from utils import setup_app, show_sidebar, track_daily_mission_progress, check_mission_eligibility
import calendar
from datetime import datetime, timedelta
import pandas as pd

setup_app()
show_sidebar()

st.title("📅 Agenda de Estudos")

if not st.session_state.user_profile:
    st.warning("Por favor, faça login para acessar sua agenda de estudos.")
    st.stop()

# Initialize study tracking in session state
if "study_days" not in st.session_state:
    st.session_state.study_days = {}  # {date_string: True/False}

if "current_study_streak" not in st.session_state:
    st.session_state.current_study_streak = 0

if "daily_missions" not in st.session_state:
    st.session_state.daily_missions = {}  # {date_string: {mission_id: completed}}

if "daily_missions_xp" not in st.session_state:
    st.session_state.daily_missions_xp = {}  # {date_string: total_xp_earned}

# Get current date
today = datetime.now()
current_month = today.month
current_year = today.year

# Display streak info
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("🔥 Ofensiva Atual", f"{st.session_state.current_study_streak} dias")

with col2:
    days_this_month = len([d for d in st.session_state.study_days if st.session_state.study_days[d] and d.startswith(f"{current_year}-{current_month:02d}")])
    st.metric("📚 Dias estudados este mês", days_this_month)

with col3:
    total_days = len([d for d in st.session_state.study_days if st.session_state.study_days[d]])
    st.metric("✅ Total de dias estudados", total_days)

st.markdown("---")

# Daily Missions Section
st.markdown("### 🎯 Missões do Dia")

today_str = f"{today.year}-{today.month:02d}-{today.day:02d}"

# Get today's progress
progress = track_daily_mission_progress()

# Define daily missions with progress tracking
daily_missions = [
    {
        "id": "mission_1", 
        "title": "📖 Estudar 15 minutos", 
        "xp": 50, 
        "icon": "📖",
        "progress": progress["study_time_minutes"],
        "goal": 15,
        "unit": "min"
    },
    {
        "id": "mission_2", 
        "title": "🎯 Completar 1 missão", 
        "xp": 100, 
        "icon": "🎯",
        "progress": progress["missions_completed"],
        "goal": 1,
        "unit": "missão"
    },
    {
        "id": "mission_3", 
        "title": "🧠 Resolver 3 problemas", 
        "xp": 75, 
        "icon": "🧠",
        "progress": progress["problems_solved"],
        "goal": 3,
        "unit": "problemas"
    },
    {
        "id": "mission_4", 
        "title": "⭐ Acertar 5 questões seguidas", 
        "xp": 150, 
        "icon": "⭐",
        "progress": progress["max_consecutive_correct"],
        "goal": 5,
        "unit": "seguidas"
    },
]

# Initialize today's missions if not exists
if today_str not in st.session_state.daily_missions:
    st.session_state.daily_missions[today_str] = {m["id"]: False for m in daily_missions}

if today_str not in st.session_state.daily_missions_xp:
    st.session_state.daily_missions_xp[today_str] = 0

# Display missions in a grid
cols = st.columns(2)
for idx, mission in enumerate(daily_missions):
    with cols[idx % 2]:
        is_completed = st.session_state.daily_missions[today_str].get(mission["id"], False)
        is_eligible = check_mission_eligibility(mission["id"])
        
        # Mission card
        if is_completed:
            st.markdown(f"""
            <div style="background: #C8E6C9; padding: 15px; border-radius: 10px; border: 2px solid #4CAF50; margin-bottom: 10px;">
                <div style="font-size: 20px; margin-bottom: 5px;">{mission['icon']} {mission['title']}</div>
                <div style="color: #2E7D32; font-weight: bold;">✅ Completada! +{mission['xp']} XP</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Show progress bar
            progress_pct = min(100, int((mission["progress"] / mission["goal"]) * 100))
            
            st.markdown(f"""
            <div style="background: white; padding: 15px; border-radius: 10px; border: 2px solid #0047AB; margin-bottom: 10px;">
                <div style="font-size: 20px; margin-bottom: 5px;">{mission['icon']} {mission['title']}</div>
                <div style="color: #0047AB; font-weight: bold;">🎁 Recompensa: +{mission['xp']} XP</div>
                <div style="margin-top: 10px;">
                    <div style="background: #e0e0e0; border-radius: 10px; height: 20px; overflow: hidden;">
                        <div style="background: #0047AB; height: 100%; width: {progress_pct}%;"></div>
                    </div>
                    <div style="text-align: center; margin-top: 5px; font-size: 14px; color: #666;">
                        {mission["progress"]}/{mission["goal"]} {mission["unit"]}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if is_eligible:
                if st.button(f"🎁 Resgatar Recompensa", key=f"claim_{mission['id']}", use_container_width=True, type="primary"):
                    st.session_state.daily_missions[today_str][mission["id"]] = True
                    st.session_state.daily_missions_xp[today_str] += mission["xp"]
                    st.session_state.xp += mission["xp"]
                    st.success(f"🎉 Missão resgatada! +{mission['xp']} XP")
                    st.balloons()
                    st.rerun()
            else:
                st.button(f"🔒 Continue progredindo", key=f"locked_{mission['id']}", use_container_width=True, disabled=True)

# Show total XP earned today
total_xp_today = st.session_state.daily_missions_xp.get(today_str, 0)
completed_today = sum(1 for m in st.session_state.daily_missions[today_str].values() if m)

st.markdown(f"""
<div style="background: linear-gradient(135deg, #0047AB 0%, #00BFFF 100%); padding: 20px; border-radius: 15px; text-align: center; margin: 20px 0;">
    <div style="color: white; font-size: 18px; font-weight: bold;">💰 XP Ganho Hoje: {total_xp_today}</div>
    <div style="color: white; font-size: 14px; margin-top: 5px;">Missões completadas: {completed_today}/4</div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# Month selector
col_month, col_year = st.columns(2)
with col_month:
    selected_month = st.selectbox(
        "Mês",
        range(1, 13),
        index=current_month - 1,
        format_func=lambda x: calendar.month_name[x]
    )

with col_year:
    selected_year = st.selectbox(
        "Ano",
        range(current_year - 1, current_year + 2),
        index=1
    )

# Generate calendar
st.markdown(f"### {calendar.month_name[selected_month]} {selected_year}")

# Get calendar for selected month
cal = calendar.monthcalendar(selected_year, selected_month)

# Create calendar HTML
calendar_html = """
<style>
.calendar-container {
    width: 100%;
    max-width: 800px;
    margin: 0 auto;
}
.calendar-table {
    width: 100%;
    border-collapse: collapse;
    background: white;
    border-radius: 10px;
    overflow: hidden;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}
.calendar-table th {
    background: #0047AB;
    color: white;
    padding: 15px;
    font-weight: bold;
    text-align: center;
}
.calendar-table td {
    padding: 20px;
    text-align: center;
    border: 1px solid #e0e0e0;
    position: relative;
    height: 80px;
    vertical-align: top;
}
.calendar-table td.empty {
    background: #f5f5f5;
}
.calendar-table td.today {
    background: #E0F7FA;
    border: 2px solid #0047AB;
}
.calendar-table td.studied {
    background: #C8E6C9;
}
.day-number {
    font-size: 18px;
    font-weight: bold;
    color: #333;
}
.study-badge {
    position: absolute;
    bottom: 5px;
    right: 5px;
    font-size: 24px;
}
</style>
<div class="calendar-container">
<table class="calendar-table">
<thead>
<tr>
    <th>Dom</th>
    <th>Seg</th>
    <th>Ter</th>
    <th>Qua</th>
    <th>Qui</th>
    <th>Sex</th>
    <th>Sáb</th>
</tr>
</thead>
<tbody>
"""

# Add calendar rows
for week in cal:
    calendar_html += "<tr>"
    for day in week:
        if day == 0:
            calendar_html += '<td class="empty"></td>'
        else:
            date_str = f"{selected_year}-{selected_month:02d}-{day:02d}"
            is_today = (day == today.day and selected_month == today.month and selected_year == today.year)
            is_studied = st.session_state.study_days.get(date_str, False)
            
            classes = []
            if is_today:
                classes.append("today")
            if is_studied:
                classes.append("studied")
            
            class_str = ' '.join(classes)
            
            badge = "✅" if is_studied else ""
            
            calendar_html += f'<td class="{class_str}"><div class="day-number">{day}</div><div class="study-badge">{badge}</div></td>'
    calendar_html += "</tr>"

calendar_html += """
</tbody>
</table>
</div>
"""

st.markdown(calendar_html, unsafe_allow_html=True)

st.markdown("---")

st.markdown("### 📚 Marcar Estudo do Dia")


# Mark today as studied (Automatic now) -> Trigger Redeploy Fix
if st.session_state.study_days.get(today_str, False):
    st.success(f"✅ Dia marcado automaticamente! Ofensiva: {st.session_state.current_study_streak} dias! 🔥")
else:
    # Fallback just in case auto-mark failed (shouldn't happen on login)
    if st.button("✅ Marcar Presença Manualmente", type="primary"):
        from utils import mark_today_as_studied
        mark_today_as_studied()
        st.rerun()


st.markdown("---")
st.markdown("### 💡 Dicas de Estudo Personalizadas")

methodology = st.session_state.user_profile.get("methodology", "Padrão")
st.info(f"**Sua metodologia:** {methodology}")

tips = [
    "📖 Estude um pouco todos os dias, mesmo que sejam apenas 15 minutos!",
    "🎯 Complete pelo menos uma missão por dia para manter sua ofensiva.",
    "🧠 Revise os conceitos que você já aprendeu regularmente.",
    "💪 Desafie-se com problemas um pouco mais difíceis gradualmente.",
    "🎨 Use seus interesses para tornar a matemática mais divertida!"
]

for tip in tips:
    st.markdown(f"- {tip}")
