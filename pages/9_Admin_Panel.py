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

def get_neural_network_html(function_name, is_fallback):
    func_js = f"'{function_name}'" if function_name else "null"
    is_fallback_js = "true" if is_fallback else "false"
    
    html = f"""
<!DOCTYPE html>
<html>
<head>
<style>
body {{
    background-color: #0b0f19;
    margin: 0;
    overflow: hidden;
    font-family: 'Segoe UI', Roboto, sans-serif;
    color: #e6edf3;
}}
.network-container {{
    width: 100%;
    height: 380px;
    position: relative;
}}
svg {{
    width: 100%;
    height: 100%;
}}
.node {{
    fill: #111827;
    stroke: #374151;
    stroke-width: 2px;
    transition: all 0.5s ease;
}}
.node.input {{
    stroke: #9c27b0;
    fill: rgba(156, 39, 176, 0.1);
}}
.node.hidden {{
    stroke: #3b82f6;
    fill: rgba(59, 130, 246, 0.1);
}}
.node.output {{
    stroke: #06b6d4;
    fill: rgba(6, 182, 212, 0.1);
}}
.node.active-input {{
    fill: #9c27b0;
    stroke: #c084fc;
    filter: drop-shadow(0 0 8px #c084fc);
}}
.node.active-hidden {{
    fill: #2563eb;
    stroke: #60a5fa;
    filter: drop-shadow(0 0 8px #60a5fa);
}}
.node.active-output {{
    fill: #0891b2;
    stroke: #22d3ee;
    filter: drop-shadow(0 0 8px #22d3ee);
}}
.node.active-output.fallback {{
    fill: #dc2626;
    stroke: #f87171;
    filter: drop-shadow(0 0 8px #f87171);
}}
.link {{
    stroke: rgba(55, 65, 81, 0.35);
    stroke-width: 1px;
    fill: none;
    transition: stroke 0.5s ease, stroke-width 0.5s ease;
}}
.link.active {{
    stroke: rgba(34, 211, 238, 0.75);
    stroke-width: 2.5px;
    stroke-dasharray: 6 6;
    animation: dash 0.8s linear infinite;
}}
.link.active.fallback {{
    stroke: rgba(248, 113, 113, 0.75);
}}
@keyframes dash {{
    to {{
        stroke-dashoffset: -20;
    }}
}}
.label {{
    fill: #9ca3af;
    font-size: 10px;
    font-weight: 500;
    pointer-events: none;
}}
.label.active {{
    fill: #ffffff;
    font-weight: bold;
}}
.layer-title {{
    fill: #6b7280;
    font-size: 11px;
    font-weight: bold;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}}
</style>
</head>
<body>
<div class="network-container">
<svg id="neural-net" viewBox="0 0 800 380" preserveAspectRatio="xMidYMid meet">
    <text x="100" y="30" class="layer-title" text-anchor="middle">Entrada</text>
    <text x="300" y="30" class="layer-title" text-anchor="middle">Processamento (I)</text>
    <text x="500" y="30" class="layer-title" text-anchor="middle">Processamento (II)</text>
    <text x="700" y="30" class="layer-title" text-anchor="middle">Saída</text>
    
    <g id="links"></g>
    <g id="nodes"></g>
</svg>
</div>

<script>
const nodesConfig = [
    {{ id: 'i1', x: 100, y: 100, label: 'Contexto', type: 'input' }},
    {{ id: 'i2', x: 100, y: 190, label: 'Perfil Aluno', type: 'input' }},
    {{ id: 'i3', x: 100, y: 280, label: 'Entrada Aluno', type: 'input' }},
    
    {{ id: 'h1_1', x: 300, y: 70, label: 'Prompt Builder', type: 'hidden' }},
    {{ id: 'h1_2', x: 300, y: 150, label: 'Model Router', type: 'hidden' }},
    {{ id: 'h1_3', x: 300, y: 230, label: 'Chain of Thought', type: 'hidden' }},
    {{ id: 'h1_4', x: 300, y: 310, label: 'ZDP Adaptative', type: 'hidden' }},
    
    {{ id: 'h2_1', x: 500, y: 70, label: 'Cognitive Scaffold', type: 'hidden' }},
    {{ id: 'h2_2', x: 500, y: 150, label: 'Socratic Dialogue', type: 'hidden' }},
    {{ id: 'h2_3', x: 500, y: 230, label: 'BNCC Mapping', type: 'hidden' }},
    {{ id: 'h2_4', x: 500, y: 310, label: 'JSON Parser', type: 'hidden' }},
    
    {{ id: 'o1', x: 700, y: 100, label: 'Missions / Met', type: 'output' }},
    {{ id: 'o2', x: 700, y: 190, label: 'Problem / Hint', type: 'output' }},
    {{ id: 'o3', x: 700, y: 280, label: 'Feedback/Diagnostic', type: 'output' }}
];

const paths = {{
    'generate_methodology': {{
        nodes: ['i2', 'h1_1', 'h1_4', 'h2_4', 'o1'],
        links: [['i2', 'h1_1'], ['i2', 'h1_4'], ['h1_1', 'h2_4'], ['h1_4', 'h2_4'], ['h2_4', 'o1']]
    }},
    'generate_missions': {{
        nodes: ['i1', 'i2', 'h1_1', 'h1_2', 'h1_4', 'h2_3', 'h2_4', 'o1'],
        links: [['i1', 'h1_1'], ['i2', 'h1_4'], ['h1_1', 'h2_3'], ['h1_4', 'h2_4'], ['h2_3', 'o1'], ['h2_4', 'o1']]
    }},
    'generate_greeting': {{
        nodes: ['i2', 'h1_1', 'h2_1', 'o1'],
        links: [['i2', 'h1_1'], ['h1_1', 'h2_1'], ['h2_1', 'o1']]
    }},
    'generate_problem': {{
        nodes: ['i1', 'i2', 'h1_1', 'h1_3', 'h2_1', 'h2_3', 'h2_4', 'o2'],
        links: [['i1', 'h1_3'], ['i2', 'h1_1'], ['h1_3', 'h2_1'], ['h1_1', 'h2_3'], ['h2_1', 'o2'], ['h2_3', 'h2_4'], ['h2_4', 'o2']]
    }},
    'get_bncc_alignment': {{
        nodes: ['i1', 'h1_1', 'h2_3', 'h2_4', 'o2'],
        links: [['i1', 'h1_1'], ['h1_1', 'h2_3'], ['h2_3', 'h2_4'], ['h2_4', 'o2']]
    }},
    'validate_answer': {{
        nodes: ['i1', 'i3', 'h1_2', 'h1_4', 'h2_2', 'h2_4', 'o3'],
        links: [['i3', 'h1_2'], ['i1', 'h1_4'], ['h1_2', 'h2_2'], ['h1_4', 'h2_4'], ['h2_2', 'o3'], ['h2_4', 'o3']]
    }},
    'generate_next_mission': {{
        nodes: ['i1', 'i2', 'h1_1', 'h1_4', 'h2_4', 'o1'],
        links: [['i1', 'h1_1'], ['i2', 'h1_4'], ['h1_1', 'h2_4'], ['h1_4', 'h2_4'], ['h2_4', 'o1']]
    }}
}};

const linksGroup = document.getElementById('links');
const nodesGroup = document.getElementById('nodes');

const activeFunc = {func_js};
const isFallback = {is_fallback_js};
const activePath = paths[activeFunc] || {{ nodes: [], links: [] }};

const layers = [[], [], [], []];
nodesConfig.forEach(n => {{
    if (n.type === 'input') layers[0].push(n);
    else if (n.id.startsWith('h1_')) layers[1].push(n);
    else if (n.id.startsWith('h2_')) layers[2].push(n);
    else layers[3].push(n);
}});

// Render Links
for (let l = 0; l < 3; l++) {{
    const currentLayer = layers[l];
    const nextLayer = layers[l+1];
    
    currentLayer.forEach(n1 => {{
        nextLayer.forEach(n2 => {{
            const isLinkActive = activePath.links.some(link => link[0] === n1.id && link[1] === n2.id);
            const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
            line.setAttribute('x1', n1.x);
            line.setAttribute('y1', n1.y);
            line.setAttribute('x2', n2.x);
            line.setAttribute('y2', n2.y);
            line.setAttribute('id', `link-${{n1.id}}-${{n2.id}}`);
            
            let classStr = 'link';
            if (isLinkActive) {{
                classStr += ' active';
                if (isFallback) classStr += ' fallback';
            }}
            line.setAttribute('class', classStr);
            linksGroup.appendChild(line);
        }});
    }});
}}

// Render Nodes & Labels
nodesConfig.forEach(n => {{
    const isNodeActive = activePath.nodes.includes(n.id);
    
    const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    
    const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    circle.setAttribute('cx', n.x);
    circle.setAttribute('cy', n.y);
    circle.setAttribute('r', isNodeActive ? 13 : 9);
    circle.setAttribute('id', `circle-${{n.id}}`);
    
    let classStr = `node ${{n.type}}`;
    if (isNodeActive) {{
        if (n.type === 'input') classStr += ' active-input';
        else if (n.type === 'hidden') classStr += ' active-hidden';
        else if (n.type === 'output') {{
            classStr += ' active-output';
            if (isFallback) classStr += ' fallback';
        }}
    }}
    circle.setAttribute('class', classStr);
    g.appendChild(circle);
    
    const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    text.setAttribute('x', n.x);
    text.setAttribute('y', n.y + 24);
    text.setAttribute('class', `label ${{isNodeActive ? 'active' : ''}}`);
    text.setAttribute('text-anchor', 'middle');
    text.textContent = n.label;
    g.appendChild(text);
    
    nodesGroup.appendChild(g);
}});

if (!activeFunc || !paths[activeFunc]) {{
    let lastActivePath = null;
    const animateIdle = () => {{
        if (lastActivePath) {{
            lastActivePath.links.forEach(link => {{
                const el = document.getElementById(`link-${{link[0]}}-${{link[1]}}`);
                if (el) el.setAttribute('class', 'link');
            }});
            lastActivePath.nodes.forEach(nid => {{
                const el = document.getElementById(`circle-${{nid}}`);
                if (el) {{
                    const baseType = el.className.baseVal.split(' ')[1];
                    el.setAttribute('class', `node ${{baseType}}`);
                    el.setAttribute('r', 9);
                }}
            }});
        }}
        
        const keys = Object.keys(paths);
        const randomKey = keys[Math.floor(Math.random() * keys.length)];
        const path = paths[randomKey];
        lastActivePath = path;
        
        path.links.forEach(link => {{
            const el = document.getElementById(`link-${{link[0]}}-${{link[1]}}`);
            if (el) el.setAttribute('class', 'link active');
        }});
        path.nodes.forEach(nid => {{
            const el = document.getElementById(`circle-${{nid}}`);
            if (el) {{
                const baseType = el.className.baseVal.split(' ')[1];
                el.setAttribute('class', `node ${{baseType}} active-${{baseType}}`);
                el.setAttribute('r', 13);
            }}
        }});
    }};
    
    animateIdle();
    setInterval(animateIdle, 2500);
}}
</script>
</body>
</html>
"""
    return html


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
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard Geral", "🎯 Monitoramento de Aprendizado (BNCC)", "👥 Gerenciar Usuários", "🧠 Monitoramento da IA (Rede Neural)"])
    
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
                                    
    with tab4:
        st.header("🧠 Monitoramento de Agentes e Rede Neural da IA")
        st.markdown("Acompanhe em tempo real o fluxo de decisões, rotas e ativações socráticas que a inteligência artificial do MatemAI executa.")
        
        # Load AI Logs
        with st.spinner("Carregando logs da IA..."):
            ai_logs = db.get_ai_logs(limit=25)
            
        if not ai_logs:
            st.info("Nenhuma chamada de IA registrada no banco de dados ainda. O sistema passará a armazenar e mapear as ativações a partir de novos usos.")
            
            # Show empty/idle neural network
            html_code = get_neural_network_html(None, False)
            st.components.v1.html(html_code, height=400)
        else:
            # Layout
            col_net, col_info = st.columns([5, 4])
            
            # Create list of labels
            log_labels = []
            for idx, log in enumerate(ai_logs):
                status_emoji = "🟢" if log['status'] == "success" else "🔴"
                log_labels.append(f"{status_emoji} [{log['timestamp']}] {log['function_name']} ({log['model_name']}) - Latência: {log['duration']:.2f}s")
                
            selected_log_label = st.selectbox(
                "Selecione uma Transação para Visualização:", 
                log_labels,
                index=0
            )
            
            selected_idx = log_labels.index(selected_log_label)
            selected_log = ai_logs[selected_idx]
            
            with col_net:
                st.markdown("#### Ativações da Rede Neural de Processamento")
                is_fallback = selected_log['status'] == "fallback"
                html_code = get_neural_network_html(selected_log['function_name'], is_fallback)
                st.components.v1.html(html_code, height=400)
                
            with col_info:
                st.markdown("#### Detalhes do Raciocínio (Sinapse)")
                
                status_color = "#10B981" if selected_log['status'] == "success" else "#EF4444"
                status_text = "SUCESSO" if selected_log['status'] == "success" else "FALLBACK ATIVADO"
                
                st.markdown(f"""
                <div style="background: #0f172a; padding: 20px; border-radius: 12px; border: 1px solid #1e293b; color: white;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                        <span style="font-weight: bold; color: {status_color}; font-size: 14px;">● {status_text}</span>
                        <span style="font-size: 12px; color: #94a3b8;">{selected_log['timestamp']}</span>
                    </div>
                    <div style="margin-bottom: 10px;">
                        <span style="color: #94a3b8; font-size: 12px;">FUNÇÃO EXECUTADA</span><br>
                        <strong style="color: #38bdf8; font-size: 16px;">{selected_log['function_name']}</strong>
                    </div>
                    <div style="margin-bottom: 10px;">
                        <span style="color: #94a3b8; font-size: 12px;">MODELO LLM</span><br>
                        <strong style="color: #a855f7;">{selected_log['model_name']}</strong>
                    </div>
                    <div style="margin-bottom: 15px;">
                        <span style="color: #94a3b8; font-size: 12px;">LATÊNCIA / VELOCIDADE</span><br>
                        <strong>⏱️ {selected_log['duration']:.3f} segundos</strong>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                st.write("")
                with st.expander("📥 Parâmetros de Entrada (Input Context)", expanded=True):
                    st.code(selected_log['input'], language="text")
                    
                with st.expander("📤 Resposta Gerada (Output JSON/Text)", expanded=True):
                    st.code(selected_log['output'], language="json" if selected_log['output'].strip().startswith("{") or selected_log['output'].strip().startswith("[") else "text")
            
            st.markdown("### 📋 Histórico Recente de Transações da IA")
            log_df = pd.DataFrame(ai_logs)
            st.dataframe(
                log_df[['timestamp', 'function_name', 'model_name', 'status', 'duration']],
                use_container_width=True,
                hide_index=True
            )

if __name__ == "__main__":
    main()
