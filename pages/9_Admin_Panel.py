import streamlit as st
import pandas as pd
import plotly.express as px
from database import get_database
from auth import check_authentication

# Configuração da página
st.set_page_config(
    page_title="Painel Administrativo",
    page_icon="🛡️",
    layout="wide"
)

# Constantes
ADMIN_EMAIL = "weslley.uca@gmail.com"

RECOMMENDED_SKILLS = {
    "1º ano": [
        {"habilidade": "EF01MA01", "habilidade_texto": "Utilizar números naturais como indicador de quantidade ou de ordem em diferentes situações cotidianas.", "competencia": "Competência Geral 1"},
        {"habilidade": "EF01MA04", "habilidade_texto": "Contar de maneira exata ou aproximada, de dez em dez e de cem em cem, agrupando objetos de diversas formas.", "competencia": "Competência Geral 2"}
    ],
    "2º ano": [
        {"habilidade": "EF02MA01", "habilidade_texto": "Comparar e ordenar números naturais pela compreensão de características do sistema de numeração decimal.", "competencia": "Competência Geral 1"},
        {"habilidade": "EF02MA09", "habilidade_texto": "Construir sequências de números naturais em ordem crescente ou decrescente a partir de um número dado.", "competencia": "Competência Geral 3"}
    ],
    "3º ano": [
        {"habilidade": "EF03MA01", "habilidade_texto": "Ler, escrever e comparar números naturais de até quatro ordens, com base na compreensão do sistema decimal.", "competencia": "Competência Geral 1"},
        {"habilidade": "EF03MA05", "habilidade_texto": "Utilizar diferentes procedimentos de cálculo mental e escrito para resolver problemas de adição e subtração.", "competencia": "Competência Geral 2"}
    ],
    "4º ano": [
        {"habilidade": "EF04MA01", "habilidade_texto": "Ler, escrever e ordenar números naturais até a ordem das dezenas de milhar.", "competencia": "Competência Geral 1"},
        {"habilidade": "EF04MA05", "habilidade_texto": "Utilizar as propriedades das operações para desenvolver estratégias de cálculo mental com números naturais.", "competencia": "Competência Geral 2"}
    ],
    "5º ano": [
        {"habilidade": "EF05MA07", "habilidade_texto": "Resolver e elaborar problemas de adição e subtração com números naturais e com números racionais.", "competencia": "Competência Geral 1"},
        {"habilidade": "EF05MA16", "habilidade_texto": "Associar figuras geométricas espaciais a suas planificações e analisar suas características.", "competencia": "Competência Geral 2"}
    ],
    "6º ano": [
        {"habilidade": "EF06MA01", "habilidade_texto": "Comparar e ordenar números naturais e racionais em diferentes contextos e associá-los a pontos na reta.", "competencia": "Competência Geral 1"},
        {"habilidade": "EF06MA10", "habilidade_texto": "Resolver e elaborar problemas que envolvam adição ou subtração com números racionais positivos na forma decimal.", "competencia": "Competência Geral 2"},
        {"habilidade": "EF06MA24", "habilidade_texto": "Determinar a probabilidade de ocorrência de um resultado em experimentos aleatórios simples.", "competencia": "Competência Geral 3"}
    ],
    "7º ano": [
        {"habilidade": "EF07MA01", "habilidade_texto": "Resolver e elaborar problemas com números inteiros que envolvam as operações de adição, subtração, multiplicação, divisão e potenciação.", "competencia": "Competência Geral 1"},
        {"habilidade": "EF07MA10", "habilidade_texto": "Comparar e ordenar números racionais em diferentes contextos.", "competencia": "Competência Geral 2"}
    ],
    "8º ano": [
        {"habilidade": "EF08MA01", "habilidade_texto": "Efetuar cálculos com potências expoentes inteiros e aplicá-los em situações-problema.", "competencia": "Competência Geral 1"},
        {"habilidade": "EF08MA07", "habilidade_texto": "Resolver e elaborar problemas que envolvam o cálculo de porcentagens e juros simples.", "competencia": "Competência Geral 2"}
    ],
    "9º ano": [
        {"habilidade": "EF09MA01", "habilidade_texto": "Reconhecer e empregar a notação científica para expressar e comparar grandezas muito grandes ou muito pequenas.", "competencia": "Competência Geral 1"},
        {"habilidade": "EF09MA07", "habilidade_texto": "Resolver problemas que envolvam equações do segundo grau por meio de diferentes estratégias.", "competencia": "Competência Geral 2"},
        {"habilidade": "EF09MA18", "habilidade_texto": "Resolver e elaborar problemas que envolvam o cálculo de volume de prismas, pirâmides, cilindros e cones.", "competencia": "Competência Geral 3"}
    ]
}

def check_admin_access():
    """Verifica se o usuário atual é o administrador"""
    if not check_authentication():
        st.warning("Por favor, faça login para acessar esta página.")
        st.stop()
        
    user_email = st.session_state.user_profile.get("email")
    if user_email != ADMIN_EMAIL:
        st.error("⛔ Acesso Negado. Você não tem permissão para acessar esta página.")
        st.stop()

def main():
    check_admin_access()
    
    st.title("🛡️ Painel Administrativo")
    st.markdown(f"Bem-vindo, **{st.session_state.user_profile.get('name')}**!")
    
    db = get_database()
    
    # Carregar dados
    with st.spinner("Carregando dados dos usuários..."):
        users = db.get_all_users()
        
    if not users:
        st.warning("Nenhum usuário encontrado ou erro ao carregar dados.")
        return

    df = pd.DataFrame(users)
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["📊 Dashboard Geral", "🎯 Monitoramento de Aprendizado (BNCC)", "👥 Gerenciar Usuários"])
    
    with tab1:
        st.header("Visão Geral do Desempenho Educacional")
        
        # Métricas Principais
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total de Usuários", len(df))
        with col2:
            avg_xp = df['xp'].mean()
            st.metric("Média de XP", f"{avg_xp:.0f}")
        with col3:
            avg_level = df['level'].mean()
            st.metric("Nível Médio", f"{avg_level:.1f}")
        with col4:
            engaged = len(df[df['xp'] > 0])
            st.metric("Usuários Engajados", engaged)
            
        st.divider()
        
        # Gráficos
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            st.subheader("Distribuição de Níveis")
            level_counts = df['level'].value_counts().reset_index()
            level_counts.columns = ['Nível', 'Quantidade']
            fig_levels = px.bar(level_counts, x='Nível', y='Quantidade', color='Quantidade',
                                title="Usuários por Nível", color_continuous_scale='Viridis')
            st.plotly_chart(fig_levels, use_container_width=True)
            
        with col_chart2:
            st.subheader("Distribuição de XP")
            fig_xp = px.histogram(df, x="xp", nbins=20, title="Distribuição de XP dos Usuários",
                                  color_discrete_sequence=['#4CAF50'])
            st.plotly_chart(fig_xp, use_container_width=True)
            
        # Top Escolas (se houver dados)
        if 'school' in df.columns and df['school'].nunique() > 1:
            st.subheader("Top Escolas por XP Total")
            school_xp = df.groupby('school')['xp'].sum().sort_values(ascending=False).head(10).reset_index()
            fig_school = px.bar(school_xp, x='school', y='xp', title="XP Total por Escola")
            st.plotly_chart(fig_school, use_container_width=True)

    with tab2:
        st.header("Monitoramento de Aprendizado da BNCC")
        
        # Processar dados das habilidades completadas
        skills_records = []
        for index, row in df.iterrows():
            user_skills = row.get('completed_bncc_skills', {})
            if isinstance(user_skills, dict):
                for mission_id, skill_info in user_skills.items():
                    if isinstance(skill_info, dict):
                        skills_records.append({
                            'email': row['email'],
                            'student_name': row['name'],
                            'student_nickname': row['nickname'],
                            'student_school': row['school'],
                            'student_school_year': row.get('school_year', 'N/A'),
                            'student_level': row['level'],
                            'student_xp': row['xp'],
                            'habilidade': skill_info.get('habilidade', 'N/A'),
                            'habilidade_texto': skill_info.get('habilidade_texto', 'N/A'),
                            'competencia': skill_info.get('competencia', 'N/A'),
                            'competencia_texto': skill_info.get('competencia_texto', 'N/A'),
                            'mission_id': mission_id
                        })

        if skills_records:
            skills_df = pd.DataFrame(skills_records)
        else:
            skills_df = pd.DataFrame(columns=[
                'email', 'student_name', 'student_nickname', 'student_school', 
                'student_school_year', 'student_level', 'student_xp', 
                'habilidade', 'habilidade_texto', 'competencia', 
                'competencia_texto', 'mission_id'
            ])

        # Métricas Gerais de Aprendizado
        col_m1, col_m2, col_m3 = st.columns(3)
        total_students = len(df)
        
        with col_m1:
            total_unique_skills = skills_df['habilidade'].nunique()
            st.metric("Habilidades Únicas Desenvolvidas", total_unique_skills)
        with col_m2:
            avg_skills = len(skills_df) / total_students if total_students > 0 else 0
            st.metric("Média de Habilidades por Aluno", f"{avg_skills:.1f}")
        with col_m3:
            if not skills_df.empty:
                most_frequent_skill = skills_df['habilidade'].mode().iloc[0]
                count_most_frequent = skills_df[skills_df['habilidade'] == most_frequent_skill]['email'].nunique()
                st.metric("Habilidade Mais Desenvolvida", most_frequent_skill, f"{count_most_frequent} alunos")
            else:
                st.metric("Habilidade Mais Desenvolvida", "Nenhuma")
                
        st.divider()
        
        if skills_df.empty:
            st.info("Nenhuma habilidade BNCC registrada pelos alunos ainda. As habilidades são registradas quando os alunos completam as missões.")
        else:
            # 1. Análise detalhada por habilidade específica
            st.subheader("🎯 Detalhamento por Habilidade BNCC")
            
            # Agrupar informações únicas de habilidade para exibição no selectbox
            skill_info_map = {}
            for hab in sorted(skills_df['habilidade'].unique()):
                hab_df = skills_df[skills_df['habilidade'] == hab]
                desc = hab_df['habilidade_texto'].iloc[0]
                comp = hab_df['competencia'].iloc[0]
                skill_info_map[hab] = {"desc": desc, "competencia": comp}
            
            skill_options = [f"{hab} - {info['desc'][:60]}..." for hab, info in skill_info_map.items()]
            selected_option = st.selectbox("Selecione uma habilidade para analisar:", skill_options)
            
            if selected_option:
                selected_hab = selected_option.split(" - ")[0]
                selected_info = skill_info_map[selected_hab]
                
                # Exibir Banner Estilizado
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #4F46E5 0%, #3B82F6 100%); padding: 25px; border-radius: 15px; color: white; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(59, 130, 246, 0.2);">
                    <h3 style="margin: 0 0 10px 0; color: #FFF; font-size: 20px; font-weight: 700;">📚 Habilidade: {selected_hab}</h3>
                    <p style="margin: 0 0 15px 0; font-size: 15px; line-height: 1.6; opacity: 0.95;">{selected_info['desc']}</p>
                    <div style="background: rgba(255,255,255,0.2); padding: 8px 12px; border-radius: 8px; display: inline-block;">
                        <span style="font-weight: 600; font-size: 14px;">🎯 {selected_info['competencia']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                hab_students = skills_df[skills_df['habilidade'] == selected_hab]
                num_completed = hab_students['email'].nunique()
                pct_completed = (num_completed / total_students) * 100 if total_students > 0 else 0
                
                # Exibir métricas da habilidade
                col_stat1, col_stat2 = st.columns(2)
                with col_stat1:
                    st.markdown(f"""
                    <div style="background: #F8FAFC; border-left: 5px solid #10B981; padding: 15px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                        <span style="font-size: 12px; color: #64748B; font-weight: bold; text-transform: uppercase; letter-spacing: 0.05em;">Taxa de Domínio</span>
                        <h2 style="margin: 5px 0; color: #059669; font-size: 24px; font-weight: 700;">{num_completed} de {total_students} alunos</h2>
                        <span style="font-size: 14px; font-weight: 600; color: #334155;">{pct_completed:.1f}% de todos os alunos cadastrados</span>
                    </div>
                    """, unsafe_allow_html=True)
                with col_stat2:
                    avg_xp_all = df['xp'].mean()
                    avg_xp_completed = hab_students['student_xp'].mean()
                    diff_xp = avg_xp_completed - avg_xp_all
                    diff_color = "#10B981" if diff_xp >= 0 else "#EF4444"
                    diff_sign = "+" if diff_xp >= 0 else ""
                    
                    st.markdown(f"""
                    <div style="background: #F8FAFC; border-left: 5px solid #3B82F6; padding: 15px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                        <span style="font-size: 12px; color: #64748B; font-weight: bold; text-transform: uppercase; letter-spacing: 0.05em;">XP Médio dos Alunos</span>
                        <h2 style="margin: 5px 0; color: #2563EB; font-size: 24px; font-weight: 700;">{avg_xp_completed:.0f} XP</h2>
                        <span style="font-size: 14px; color: {diff_color}; font-weight: 600;">Diferença da média da turma: {diff_sign}{diff_xp:.0f} XP</span>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.write("")
                
                # Detalhes visuais e tabela de alunos
                col_left, col_right = st.columns([5, 4])
                
                with col_left:
                    st.markdown("👥 **Alunos que completaram esta habilidade:**")
                    table_data = hab_students[['student_name', 'student_nickname', 'email', 'student_school', 'student_school_year', 'student_level', 'student_xp']].copy()
                    table_data.columns = ['Nome', 'Apelido', 'E-mail', 'Escola', 'Série', 'Nível', 'XP']
                    st.dataframe(table_data, use_container_width=True, hide_index=True)
                    
                with col_right:
                    st.markdown("📊 **Distribuição por Série (Ano Escolar):**")
                    year_counts = hab_students['student_school_year'].value_counts().reset_index()
                    year_counts.columns = ['Série', 'Alunos']
                    fig_years = px.bar(
                        year_counts, 
                        x='Série', 
                        y='Alunos', 
                        color='Alunos',
                        color_continuous_scale='Blues',
                        labels={'Alunos': 'Qtd Alunos'}
                    )
                    fig_years.update_layout(height=260, margin=dict(l=10, r=10, t=10, b=10))
                    st.plotly_chart(fig_years, use_container_width=True)
            
            st.divider()
            
            # 2. Matriz de Habilidades BNCC Geral
            st.subheader("📋 Matriz Geral de Desenvolvimento BNCC")
            
            skills_summary = []
            for hab in skills_df['habilidade'].unique():
                hab_df = skills_df[skills_df['habilidade'] == hab]
                desc = hab_df['habilidade_texto'].iloc[0]
                comp = hab_df['competencia'].iloc[0]
                count = hab_df['email'].nunique()
                pct = (count / total_students) * 100 if total_students > 0 else 0
                
                if pct > 20:
                    status = "🟢 Amplamente Desenvolvida"
                elif pct >= 5:
                    status = "🟡 Em Desenvolvimento"
                else:
                    status = "🔴 Pouco Desenvolvida"
                    
                skills_summary.append({
                    'Código': hab,
                    'Descrição da Habilidade': desc,
                    'Competência': comp,
                    'Qtd. Conclusões': count,
                    '% de Alunos': f"{pct:.1f}%",
                    'Status': status,
                    'raw_pct': pct
                })
                
            skills_summary_df = pd.DataFrame(skills_summary).sort_values(by='raw_pct', ascending=False)
            
            st.dataframe(
                skills_summary_df[['Código', 'Descrição da Habilidade', 'Competência', 'Qtd. Conclusões', '% de Alunos', 'Status']],
                use_container_width=True,
                hide_index=True
            )
            
            # Gráficos gerais da aba
            col_chart1, col_chart2 = st.columns(2)
            with col_chart1:
                st.markdown("📊 **Top 10 Habilidades Mais Desenvolvidas:**")
                top10_df = skills_summary_df.head(10)
                fig_top = px.bar(
                    top10_df, 
                    x='Código', 
                    y='Qtd. Conclusões', 
                    color='Qtd. Conclusões',
                    color_continuous_scale='Viridis',
                    labels={'Qtd. Conclusões': 'Qtd Alunos'}
                )
                st.plotly_chart(fig_top, use_container_width=True)
                
            with col_chart2:
                st.markdown("📊 **Habilidades por Status de Desenvolvimento:**")
                status_counts = skills_summary_df['Status'].value_counts().reset_index()
                status_counts.columns = ['Status', 'Quantidade']
                fig_stat = px.bar(
                    status_counts, 
                    x='Status', 
                    y='Quantidade', 
                    color='Status',
                    color_discrete_map={
                        "🟢 Amplamente Desenvolvida": "#10B981",
                        "🟡 Em Desenvolvimento": "#F59E0B",
                        "🔴 Pouco Desenvolvida": "#EF4444"
                    }
                )
                st.plotly_chart(fig_stat, use_container_width=True)

    with tab3:
        st.header("Gerenciamento de Contas")
        
        # Filtros e Pesquisa
        search_term = st.text_input("🔍 Pesquisar por nome ou email", "")
        
        if search_term:
            filtered_df = df[df['name'].str.contains(search_term, case=False) | 
                             df['email'].str.contains(search_term, case=False)]
        else:
            filtered_df = df
            
        # Tabela de Usuários
        st.dataframe(
            filtered_df[['name', 'nickname', 'email', 'level', 'xp', 'school', 'last_login']],
            use_container_width=True,
            hide_index=True
        )
        
        st.divider()
        
        # Ações em Usuário Específico
        st.subheader("✏️ Editar / Remover Usuário")
        
        selected_email = st.selectbox("Selecione um usuário para gerenciar:", filtered_df['email'].unique())
        
        if selected_email:
            user_data = filtered_df[filtered_df['email'] == selected_email].iloc[0]
            
            with st.expander(f"Gerenciar: {user_data['name']} ({selected_email})", expanded=True):
                sub_tab1, sub_tab2 = st.tabs(["📊 Relatório de Aprendizagem (BNCC)", "⚙️ Configurações da Conta"])
                
                with sub_tab1:
                    st.subheader(f"Desempenho Acadêmico de {user_data['name']}")
                    
                    # Estatísticas Rápidas
                    col_stu1, col_stu2, col_stu3, col_stu4 = st.columns(4)
                    with col_stu1:
                        st.metric("XP Total", user_data['xp'])
                    with col_stu2:
                        st.metric("Nível", user_data['level'])
                    with col_stu3:
                        st.metric("Exercícios Resolvidos", user_data.get('exercises_completed_count', 0))
                    with col_stu4:
                        streak = user_data.get('current_streak', 0)
                        st.metric("Ofensiva de Acertos", f"🔥 {streak}")
                        
                    st.write(f"🏫 **Escola:** {user_data.get('school', 'N/A')} | 📅 **Série:** {user_data.get('school_year', 'N/A')} | 🎂 **Idade:** {user_data.get('age', 'N/A') if pd.notna(user_data.get('age')) else 'N/A'} anos | ❤️ **Gosto por Matemática:** {user_data.get('confidence', 'N/A')}/10")
                    
                    st.divider()
                    
                    # Obter habilidades reais e tratar dados simulados se necessário
                    student_skills = user_data.get('completed_bncc_skills', {})
                    is_simulated = False
                    
                    # Se vazio, gerar dados simulados (fake) determinísticos com base na série do aluno
                    if not student_skills:
                        is_simulated = True
                        school_year = user_data.get('school_year', '6º ano')
                        rec_list = RECOMMENDED_SKILLS.get(school_year, RECOMMENDED_SKILLS["6º ano"])
                        
                        student_skills = {}
                        # Simular que completou 2 habilidades recomendadas
                        for i, item in enumerate(rec_list[:2]):
                            student_skills[f"sim_{i}"] = {
                                "habilidade": item["habilidade"],
                                "habilidade_texto": item["habilidade_texto"],
                                "competencia": item["competencia"],
                                "competencia_texto": "Desenvolvimento simulado (Demonstração)"
                            }
                    
                    # Habilidades Dominadas
                    st.markdown("### ✅ Habilidades Dominadas")
                    if is_simulated:
                        st.warning("⚠️ Este aluno ainda não possui habilidades reais registradas no banco. Exibindo **Habilidades Simuladas** com base em sua série escolar para demonstração.")
                    
                    if student_skills:
                        skills_list = []
                        for m_id, s_info in student_skills.items():
                            if isinstance(s_info, dict):
                                skills_list.append({
                                    "Código": s_info.get("habilidade", "N/A"),
                                    "Descrição": s_info.get("habilidade_texto", "N/A"),
                                    "Competência": s_info.get("competencia", "N/A"),
                                    "Origem": "Simulado 🧪" if is_simulated else "Real 🟢"
                                })
                        st.dataframe(pd.DataFrame(skills_list), use_container_width=True, hide_index=True)
                    else:
                        st.info("Nenhuma habilidade desenvolvida ainda.")
                        
                    st.divider()
                    
                    # Habilidades por Desenvolver (Falta Desenvolver pela Turma)
                    st.markdown("### 📈 Habilidades Pendentes da Série")
                    school_year = user_data.get('school_year', '6º ano')
                    
                    # Extrair habilidades de outros alunos na mesma série
                    cohort_users = df[df['school_year'] == school_year]
                    cohort_skills = []
                    
                    for idx, c_row in cohort_users.iterrows():
                        if c_row['email'] == user_data['email']:
                            continue
                        c_skills = c_row.get('completed_bncc_skills', {})
                        if isinstance(c_skills, dict):
                            for m_id, s_info in c_skills.items():
                                if isinstance(s_info, dict):
                                    cohort_skills.append({
                                        'habilidade': s_info.get('habilidade', 'N/A'),
                                        'habilidade_texto': s_info.get('habilidade_texto', 'N/A'),
                                        'competencia': s_info.get('competencia', 'N/A'),
                                        'email': c_row['email']
                                    })
                                    
                    cohort_skills_df = pd.DataFrame(cohort_skills)
                    completed_codes = {s_info.get('habilidade') for s_info in student_skills.values() if isinstance(s_info, dict)}
                    
                    if not cohort_skills_df.empty:
                        cohort_summary = []
                        total_cohort_students = cohort_users['email'].nunique() - 1
                        if total_cohort_students <= 0:
                            total_cohort_students = 1
                            
                        for hab in cohort_skills_df['habilidade'].unique():
                            if hab in completed_codes:
                                continue
                            hab_df = cohort_skills_df[cohort_skills_df['habilidade'] == hab]
                            desc = hab_df['habilidade_texto'].iloc[0]
                            comp = hab_df['competencia'].iloc[0]
                            count = hab_df['email'].nunique()
                            pct = (count / total_cohort_students) * 100
                            
                            cohort_summary.append({
                                'Código': hab,
                                'Habilidade': desc,
                                'Competência': comp,
                                '% de Alunos da Turma': f"{pct:.1f}%",
                                'Alunos Concluintes': count
                            })
                            
                        if cohort_summary:
                            st.write(f"Estas habilidades já foram dominadas por outros alunos da série **{school_year}**, mas **{user_data['name']}** ainda não as completou:")
                            st.dataframe(pd.DataFrame(cohort_summary), use_container_width=True, hide_index=True)
                        else:
                            st.success(f"🎉 Fantástico! **{user_data['name']}** dominou todas as habilidades que os demais alunos da série **{school_year}** completaram!")
                    else:
                        # Se não há dados na turma, exibir recomendações sugeridas da série do catálogo
                        rec_list = RECOMMENDED_SKILLS.get(school_year, RECOMMENDED_SKILLS.get("6º ano", []))
                        pending_recs = [item for item in rec_list if item["habilidade"] not in completed_codes]
                        
                        if pending_recs:
                            st.write(f"Não há outros alunos da série **{school_year}** com histórico de progresso. Exibindo habilidades recomendadas pelo catálogo da série para desenvolvimento:")
                            recs_display = []
                            for item in pending_recs:
                                recs_display.append({
                                    "Código": item["habilidade"],
                                    "Habilidade": item["habilidade_texto"],
                                    "Competência": item["competencia"],
                                    "Status": "Pendente 🔴"
                                })
                            st.dataframe(pd.DataFrame(recs_display), use_container_width=True, hide_index=True)
                        else:
                            st.success("Todas as habilidades sugeridas para esta série escolar já foram dominadas!")
                            
                with sub_tab2:
                    col_edit1, col_edit2 = st.columns(2)
                    
                    with col_edit1:
                        st.markdown("#### Editar Dados")
                        new_name = st.text_input("Nome", user_data['name'])
                        new_nickname = st.text_input("Nickname", user_data['nickname'])
                        new_xp = st.number_input("XP", value=int(user_data['xp']), step=10)
                        new_level = st.number_input("Nível", value=int(user_data['level']), step=1)
                        
                        if st.button("💾 Salvar Alterações"):
                            update_data = {
                                'name': new_name,
                                'nickname': new_nickname,
                                'xp': new_xp,
                                'level': new_level
                            }
                            if db.update_user_admin(selected_email, update_data):
                                st.success("Dados atualizados com sucesso!")
                                st.rerun()
                            else:
                                st.error("Erro ao atualizar dados.")
                                
                    with col_edit2:
                        st.markdown("#### Zona de Perigo")
                        st.warning("Ações irreversíveis")
                        
                        if st.button("🗑️ DELETAR USUÁRIO", type="primary"):
                            st.session_state[f'confirm_delete_{selected_email}'] = True
                            
                        if st.session_state.get(f'confirm_delete_{selected_email}'):
                            st.error("Tem certeza? Isso apagará todo o progresso e dados do usuário.")
                            if st.button("Sim, tenho certeza absoluta"):
                                if db.delete_user(selected_email):
                                    st.success(f"Usuário {selected_email} deletado.")
                                    del st.session_state[f'confirm_delete_{selected_email}']
                                    st.rerun()
                                else:
                                    st.error("Erro ao deletar usuário.")

if __name__ == "__main__":
    main()
