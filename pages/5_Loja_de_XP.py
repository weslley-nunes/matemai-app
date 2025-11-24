import streamlit as st
from utils import setup_app, show_sidebar
import time

setup_app()
show_sidebar()

st.title("🛍️ Loja de XP")
st.markdown("Troque seu esforço por recompensas incríveis!")

# --- CONFIGURAÇÃO DOS PRODUTOS ---
# Baseado em uma estimativa de 150 XP/dia
# 3 meses = ~13.500 XP
# 10 meses = ~45.000 XP

PRODUCTS = [
    {"id": 1, "name": "Gift Card Roblox R$ 50", "price": 12000, "image": "🎮", "desc": "Créditos para seus jogos favoritos."},
    {"id": 2, "name": "Gift Card Spotify 3 Meses", "price": 12000, "image": "🎵", "desc": "Música sem anúncios por 3 meses."},
    {"id": 3, "name": "Gift Card iFood R$ 50", "price": 12000, "image": "🍔", "desc": "Lanche garantido para o fim de semana."},
    {"id": 4, "name": "Skin Lendária no App", "price": 5000, "image": "✨", "desc": "Personalize seu perfil com estilo único."},
    {"id": 5, "name": "Kit Material Premium", "price": 10000, "image": "✏️", "desc": "Canetas, cadernos e post-its especiais."},
    {"id": 6, "name": "Par de Ingressos Cinema", "price": 15000, "image": "🍿", "desc": "Cinema com pipoca para você e um amigo."},
    {"id": 7, "name": "Fone Bluetooth", "price": 25000, "image": "🎧", "desc": "Som de alta qualidade sem fios."},
    {"id": 8, "name": "Power Bank 10000mAh", "price": 20000, "image": "🔋", "desc": "Nunca fique sem bateria no celular."},
    {"id": 9, "name": "Mochila Gamer", "price": 30000, "image": "🎒", "desc": "Estilo e espaço para seu setup."},
    {"id": 10, "name": "Curso Criação de Jogos", "price": 15000, "image": "💻", "desc": "Aprenda a criar seus próprios games."},
    {"id": 11, "name": "Tablet para Estudos", "price": 50000, "image": "📱", "desc": "O prêmio máximo! Dedicação total necessária."},
]

# --- ESTADO DO CARRINHO ---
if "cart" not in st.session_state:
    st.session_state.cart = []

def add_to_cart(product):
    st.session_state.cart.append(product)
    st.toast(f"{product['name']} adicionado ao carrinho!", icon="🛒")

def remove_from_cart(product_index):
    st.session_state.cart.pop(product_index)
    st.rerun()

def clear_cart():
    st.session_state.cart = []
    st.rerun()

# --- SIDEBAR INFO ---
st.sidebar.markdown("---")
st.sidebar.markdown(f"### 💰 Seu Saldo: {st.session_state.xp} XP")

# --- LAYOUT PRINCIPAL ---

# Abas para Loja e Carrinho
tab_store, tab_cart = st.tabs(["🏪 Produtos", "🛒 Carrinho"])

with tab_store:
    st.markdown("### Destaques")
    
    # Destaque do item Premium
    premium_item = PRODUCTS[-1]
    with st.container():
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%); padding: 20px; border-radius: 15px; color: black; margin-bottom: 30px; box-shadow: 0 4px 15px rgba(255, 215, 0, 0.3);">
            <div style="display: flex; align-items: center; justify-content: space-between;">
                <div>
                    <h2 style="margin:0;">🏆 {premium_item['name']}</h2>
                    <p style="font-size: 18px; margin: 5px 0;">{premium_item['desc']}</p>
                    <h3 style="margin:0;">💎 {premium_item['price']} XP</h3>
                    <p style="font-size: 12px; opacity: 0.8;">(Aprox. 10 meses de dedicação)</p>
                </div>
                <div style="font-size: 80px;">{premium_item['image']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button(f"Adicionar {premium_item['name']} ao Carrinho", key="btn_premium"):
            add_to_cart(premium_item)

    st.markdown("### Todos os Produtos")
    
    # Grid de produtos
    cols = st.columns(3)
    for i, product in enumerate(PRODUCTS[:-1]): # Exclui o premium da lista normal
        with cols[i % 3]:
            with st.container(border=True):
                st.markdown(f"<div style='text-align:center; font-size: 50px;'>{product['image']}</div>", unsafe_allow_html=True)
                st.markdown(f"**{product['name']}**")
                st.caption(product['desc'])
                st.markdown(f"**💰 {product['price']} XP**")
                
                if st.button("Adicionar", key=f"prod_{product['id']}", use_container_width=True):
                    add_to_cart(product)

with tab_cart:
    if not st.session_state.cart:
        st.info("Seu carrinho está vazio. Vá às compras! 🛍️")
    else:
        total_price = sum(item['price'] for item in st.session_state.cart)
        
        st.markdown(f"### Resumo do Pedido")
        
        for i, item in enumerate(st.session_state.cart):
            c1, c2, c3 = st.columns([1, 3, 1])
            with c1:
                st.markdown(f"<div style='font-size: 30px;'>{item['image']}</div>", unsafe_allow_html=True)
            with c2:
                st.markdown(f"**{item['name']}**")
                st.caption(f"{item['price']} XP")
            with c3:
                if st.button("❌", key=f"rem_{i}"):
                    remove_from_cart(i)
        
        st.markdown("---")
        c_tot1, c_tot2 = st.columns([3, 1])
        with c_tot1:
            st.markdown("### Total:")
        with c_tot2:
            color = "green" if st.session_state.xp >= total_price else "red"
            st.markdown(f"<h3 style='color:{color}'>{total_price} XP</h3>", unsafe_allow_html=True)
        
        if st.session_state.xp < total_price:
            st.error(f"Você precisa de mais {total_price - st.session_state.xp} XP para realizar esta troca.")
        else:
            st.success("Você tem XP suficiente! Preencha os dados para envio.")
            
            with st.form("checkout_form"):
                st.markdown("#### 📦 Dados de Envio")
                name = st.text_input("Nome Completo")
                address = st.text_input("Endereço Completo")
                cep = st.text_input("CEP")
                email = st.text_input("E-mail para contato")
                
                submitted = st.form_submit_button("✅ Confirmar Troca", type="primary", use_container_width=True)
                
                if submitted:
                    if not name or not address or not cep or not email:
                        st.error("Por favor, preencha todos os campos de envio.")
                    else:
                        # Processar compra
                        st.session_state.xp -= total_price
                        
                        # Preparar dados do pedido
                        order_data = {
                            "items": st.session_state.cart,
                            "total_price": total_price,
                            "shipping_info": {
                                "name": name,
                                "address": address,
                                "cep": cep,
                                "email": email
                            },
                            "status": "pending"
                        }
                        
                        # Salvar no Banco de Dados
                        from database import get_database
                        from utils import save_user_progress
                        
                        db = get_database()
                        email_user = st.session_state.user_profile.get("email")
                        
                        if email_user:
                            # Salvar pedido
                            db.save_order(email_user, order_data)
                            # Salvar novo saldo de XP
                            save_user_progress()
                        
                        st.session_state.cart = []
                        
                        st.balloons()
                        st.success("Troca realizada com sucesso! 🎉")
                        st.markdown(f"""
                        **Comprovante de Solicitação**
                        
                        **Itens:** {len(order_data['items'])} itens trocados.
                        **Total Descontado:** {total_price} XP
                        **Saldo Restante:** {st.session_state.xp} XP
                        
                        Enviaremos um e-mail para **{email}** com os detalhes do rastreio/resgate.
                        """)
                        time.sleep(5)
                        st.rerun()

            if st.button("🗑️ Esvaziar Carrinho"):
                clear_cart()
