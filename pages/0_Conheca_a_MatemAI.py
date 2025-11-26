import streamlit as st
from utils import setup_app, show_sidebar, get_img_as_base64
import os

# Configuração da Página
st.set_page_config(
    page_title="Conheça a MatemAI",
    page_icon="🤖",
    layout="wide"
)

# Inicialização
setup_app()
show_sidebar()

# Título Principal
st.markdown("<h1 style='text-align: center; color: #0047AB;'>Conheça a MatemAI 🤖</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #666;'>Transformando a Educação Matemática com Inteligência Artificial</h3>", unsafe_allow_html=True)

st.divider()

# Colunas para História e Imagem
col1, col2 = st.columns([1.5, 1])

with col1:
    st.markdown("### 📜 Nossa História")
    st.markdown("""
    A **MatemAI** nasceu de um sonho: tornar o aprendizado da matemática acessível, divertido e eficaz para todos. 
    
    Identificamos que cada estudante é único, com ritmos e formas de aprender diferentes. O ensino tradicional, muitas vezes, não consegue atender a essa diversidade, gerando frustração e desinteresse.
    
    Foi então que decidimos unir a **Educação** com a **Inteligência Artificial**. Criamos uma plataforma que não apenas ensina, mas *entende* você. Um tutor virtual que está sempre disponível, adapta o conteúdo às suas necessidades e transforma exercícios em missões gamificadas.
    
    Mais do que um app, somos um **Projeto Educacional Social**. Acreditamos que a educação de qualidade é um direito, e a tecnologia é a chave para democratizá-la.
    """)

with col2:
    if os.path.exists("assets/mascot.png"):
        st.image("assets/mascot.png", caption="Nosso mascote inteligente!", use_container_width=True)
    else:
        st.info("🤖 Imagine nosso mascote aqui!")

st.divider()

# Missão, Visão e Valores
st.markdown("### 🎯 Nossos Pilares")

c1, c2, c3 = st.columns(3)

with c1:
    st.container(border=True).markdown("""
    #### 🚀 Missão
    Democratizar o ensino da matemática através de uma plataforma inteligente e adaptativa, que respeita a individualidade de cada aluno e desperta o prazer em aprender.
    """)

with c2:
    st.container(border=True).markdown("""
    #### 👁️ Visão
    Ser a referência global em educação personalizada por IA, construindo um futuro onde ninguém desiste da matemática por falta de apoio ou compreensão.
    """)

with c3:
    st.container(border=True).markdown("""
    #### 💎 Valores
    *   **Inclusão:** Educação para todos.
    *   **Inovação:** Tecnologia a serviço do aprendizado.
    *   **Personalização:** Respeito ao ritmo de cada um.
    *   **Diversão:** Aprender não precisa ser chato.
    """)

st.divider()

# Chamada para Ação
st.markdown("""
<div style='text-align: center; padding: 20px; background-color: #f0f2f6; border-radius: 15px;'>
    <h3>Faça parte dessa revolução!</h3>
    <p>Comece sua jornada agora mesmo e descubra o poder da matemática personalizada.</p>
</div>
""", unsafe_allow_html=True)

if st.button("🚀 Ir para o Início", use_container_width=True, type="primary"):
    st.switch_page("app.py")
