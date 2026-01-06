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
    tab1, tab2 = st.tabs(["📊 Dashboard", "👥 Gerenciar Usuários"])
    
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
            # Usuários ativos hoje (simulado com last_login se fosse datetime, mas aqui simplificado)
            # Vamos contar usuários com XP > 0 como "Engajados"
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
                        # Confirmação simples via session state ou apenas um aviso forte
                        # Streamlit buttons resetam, então idealmente usaria um modal ou confirmação em duas etapas
                        # Aqui vamos usar um checkbox de segurança
                        st.session_state[f'confirm_delete_{selected_email}'] = True
                        
                    if st.session_state.get(f'confirm_delete_{selected_email}'):
                        st.error("Tem certeza? Isso apagará todo o progresso e dados do usuário.")
                        if st.button("Sim, tenho certeza absoluta"):
                            if db.delete_user(selected_email):
                                st.success(f"Usuário {selected_email} deletado.")
                                # Limpar estado e recarregar
                                del st.session_state[f'confirm_delete_{selected_email}']
                                st.rerun()
                            else:
                                st.error("Erro ao deletar usuário.")

if __name__ == "__main__":
    main()
