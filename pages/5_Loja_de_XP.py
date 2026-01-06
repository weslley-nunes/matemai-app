import streamlit as st
from utils import setup_app, show_sidebar, save_user_progress
from avatar_assets import get_shop_items
import time

setup_app()
show_sidebar()

st.title("🛍️ Loja de XP")
st.markdown("Personalize seu avatar com itens exclusivos!")

# --- INICIALIZAÇÃO ---
if "inventory" not in st.session_state:
    st.session_state.inventory = []

# Carregar itens da loja
shop_items = get_shop_items()

# --- FUNÇÕES ---
def buy_item(item):
    price = item['price']
    
    if st.session_state.xp >= price:
        # Deduzir XP
        st.session_state.xp -= price
        
        # Adicionar ao inventário
        if "inventory" not in st.session_state:
            st.session_state.inventory = []
        
        st.session_state.inventory.append(item['id'])
        
        # Salvar progresso
        save_user_progress()
        
        # Feedback visual
        st.balloons()
        st.success(f"Você comprou **{item['name']}**! 🎉")
        st.markdown(f"""
        <div style="text-align: center; padding: 20px; background-color: #d4edda; border-radius: 10px; margin-top: 10px;">
            <h3 style="color: #155724;">Item Desbloqueado!</h3>
            <p>Vá até <b>Meu Perfil</b> para equipar seu novo item.</p>
        </div>
        """, unsafe_allow_html=True)
        
        time.sleep(3)
        st.rerun()
    else:
        st.error(f"Você precisa de mais {price - st.session_state.xp} XP para comprar este item.")

# --- SIDEBAR INFO ---
st.sidebar.markdown("---")
st.sidebar.markdown(f"### 💰 Seu Saldo: {st.session_state.xp} XP")

# --- LAYOUT DA LOJA ---

# Agrupar itens por categoria para facilitar a navegação
categories = {
    "top": "Chapéus e Cabelos",
    "accessories": "Acessórios",
    "clothing": "Roupas",
    "eyes": "Olhos",
    "hairColor": "Cores de Cabelo",
    "mouth": "Bocas"
}

# Filtrar categorias que têm itens à venda
active_categories = {}
for item in shop_items:
    cat_key = item['category']
    if cat_key in categories:
        active_categories[cat_key] = categories[cat_key]

# Criar abas para as categorias
tabs = st.tabs(list(active_categories.values()))

for i, (cat_key, cat_name) in enumerate(active_categories.items()):
    with tabs[i]:
        # Filtrar itens desta categoria
        category_items = [item for item in shop_items if item['category'] == cat_key]
        
        # Grid de produtos
        cols = st.columns(3)
        for idx, item in enumerate(category_items):
            with cols[idx % 3]:
                with st.container(border=True):
                    st.markdown(f"### {item['name']}")
                    
                    # Verificar se já possui o item
                    is_owned = item['id'] in st.session_state.inventory
                    
                    if is_owned:
                        st.info("✅ Já possui")
                    else:
                        st.markdown(f"**💰 {item['price']} XP**")
                        
                        # Botão de compra com callback
                        if st.button(f"Comprar", key=f"buy_{item['category']}_{item['id']}", use_container_width=True):
                            buy_item(item)
                            
st.markdown("---")
st.info("💡 Dica: Complete missões diárias para ganhar mais XP e comprar itens raros!")
