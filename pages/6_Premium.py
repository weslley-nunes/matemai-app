import streamlit as st
from utils import setup_app, show_sidebar, save_user_progress
import time

setup_app()
show_sidebar()

st.title("💎 Premium & Energia")
st.markdown("Potencialize seus estudos e nunca pare de aprender!")

# --- STATUS ATUAL ---
if st.session_state.user_profile and st.session_state.user_profile.get("is_premium"):
    st.markdown("""
    <div style="background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%); padding: 20px; border-radius: 15px; text-align: center; margin-bottom: 30px; box-shadow: 0 4px 15px rgba(255, 215, 0, 0.3);">
        <h2 style="color: black; margin:0;">🌟 VOCÊ É PREMIUM!</h2>
        <p style="color: black; font-size: 18px;">Sua energia é ilimitada. Aproveite!</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Discreet Cancellation Option
    with st.expander("Gerenciar Assinatura"):
        st.write("Deseja cancelar sua assinatura Premium?")
        if st.button("Cancelar Assinatura", type="secondary"):
            st.session_state.user_profile["is_premium"] = False
            # Reset battery to standard limit logic (10)
            st.session_state.neural_battery = 10
            save_user_progress()
            st.success("Assinatura cancelada. Você voltou ao plano gratuito.")
            time.sleep(2)
            st.rerun()
else:
    st.markdown(f"""
    <div style="background: #f0f2f6; padding: 15px; border-radius: 10px; margin-bottom: 30px; display: flex; align-items: center; justify-content: space-between;">
        <div>
            <span style="font-size: 18px;">🔋 Bateria Atual:</span>
            <span style="font-size: 24px; font-weight: bold; color: {'#4CAF50' if st.session_state.neural_battery > 3 else '#F44336'};">
                {st.session_state.neural_battery}/10
            </span>
        </div>
        <div style="font-size: 14px; color: #666;">
            Recarrega amanhã
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- PLANOS ---
st.markdown("### Escolha seu plano")

col1, col2, col3 = st.columns(3)

# 1. Recarga de Emergência (Âncora)
with col1:
    with st.container(border=True):
        st.markdown("<h3 style='text-align: center; color: #555;'>Recarga Única</h3>", unsafe_allow_html=True)
        st.markdown("<div style='text-align: center; font-size: 40px;'>🔋</div>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #666;'>Encha sua bateria agora (10 energias)</p>", unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("<h2 style='text-align: center;'>R$ 4,99</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; font-size: 12px; color: #888;'>Custo alto por energia</p>", unsafe_allow_html=True)
        
        if st.button("Comprar Recarga", key="btn_refill", use_container_width=True):
            with st.spinner("Processando pagamento..."):
                time.sleep(2)
                st.session_state.neural_battery = 10
                save_user_progress()
                st.success("Bateria recarregada!")
                st.rerun()

# 2. Plano Mensal (Âncora de Preço Alto)
with col2:
    with st.container(border=True):
        st.markdown("<h3 style='text-align: center; color: #1565C0;'>Plano Mensal</h3>", unsafe_allow_html=True)
        st.markdown("<div style='text-align: center; font-size: 40px;'>📅</div>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #666;'>Energia Ilimitada com renovação mensal</p>", unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("<h2 style='text-align: center; color: #1565C0;'>R$ 49,90</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; font-size: 12px; color: #888;'>Cobrado todo mês</p>", unsafe_allow_html=True)
        
        if st.button("Assinar Mensal", key="btn_monthly", use_container_width=True):
            # Simulação de Pagamento
            with st.status("Conectando ao Mercado Pago...", expanded=True) as status:
                time.sleep(2)
                status.update(label="Pagamento Aprovado!", state="complete", expanded=False)
            
            st.balloons()
            if st.session_state.user_profile:
                st.session_state.user_profile["is_premium"] = True
                save_user_progress()
            st.success("Bem-vindo ao Premium Mensal! 🚀")
            time.sleep(2)
            st.rerun()

# 3. Plano Anual (Melhor Oferta)
with col3:
    # Destaque visual
    st.markdown("""
    <style>
    div[data-testid="column"]:nth-of-type(3) div[data-testid="stVerticalBlock"] > div {
        border: 2px solid #FFD700;
        background-color: #FFFDE7;
        transform: scale(1.05);
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        z-index: 1;
    }
    </style>
    """, unsafe_allow_html=True)
    
    with st.container(border=True):
        st.markdown("<div style='background: #FFD700; color: black; padding: 5px; border-radius: 5px; text-align: center; font-weight: bold; margin-bottom: 10px;'>MELHOR CUSTO-BENEFÍCIO</div>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center; color: #000;'>Plano Anual</h3>", unsafe_allow_html=True)
        st.markdown("<div style='text-align: center; font-size: 40px;'>👑</div>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #333; font-weight: bold;'>Energia INFINITA o ano todo</p>", unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("<p style='text-align: center; text-decoration: line-through; color: #999; margin-bottom: 0;'>De R$ 599,90</p>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center; color: #D32F2F; font-size: 24px;'>12x R$ 29,90</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; font-size: 12px; color: #555;'>Cobrança anual recorrente</p>", unsafe_allow_html=True)
        
        if st.button("ASSINAR ANUAL", key="btn_annual", type="primary", use_container_width=True):
            # Simulação de Pagamento
            with st.status("Conectando ao Mercado Pago...", expanded=True) as status:
                st.write("Gerando preferência de pagamento...")
                time.sleep(1)
                st.write("Aplicando desconto anual...")
                time.sleep(1)
                status.update(label="Pagamento Aprovado!", state="complete", expanded=False)
            
            st.balloons()
            
            # Ativar Premium
            if st.session_state.user_profile:
                st.session_state.user_profile["is_premium"] = True
                save_user_progress()
                
            st.success("Parabéns! Você garantiu 1 ano de MENTE ILIMITADA! 🚀")
            time.sleep(3)
            st.rerun()

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #888; font-size: 12px;">
    Pagamentos processados de forma segura pelo <b>Mercado Pago</b>.<br>
    Cancele a qualquer momento.
</div>
""", unsafe_allow_html=True)
