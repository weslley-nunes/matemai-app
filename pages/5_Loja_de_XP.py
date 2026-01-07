import streamlit as st
from utils import setup_app, show_sidebar, save_user_progress
from avatar_assets import get_shop_items, get_avatar_url
from database import get_database
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
def get_item_preview_url(item):
    """Gera URL do avatar com o item aplicado para preview"""
    # Pega config atual ou padrão
    current_config = st.session_state.get("avatar_config", {}).copy()
    if not current_config:
        # Fallback se não tiver config
        from avatar_assets import generate_random_avatar_config
        current_config = generate_random_avatar_config()
        
    # Aplica o item na config temporária
    current_config[item['category']] = item['id']
    
    return get_avatar_url(current_config)

def equip_item(item):
    """Equipa o item e salva no banco"""
    if "avatar_config" not in st.session_state:
        st.session_state.avatar_config = {}
        
    # Atualiza config local
    st.session_state.avatar_config[item['category']] = item['id']
    
    # Gera nova URL
    new_avatar_url = get_avatar_url(st.session_state.avatar_config)
    
    # Salva no banco
    db = get_database()
    email = st.session_state.user_profile.get("email")
    
    if db.save_avatar_config(email, st.session_state.avatar_config, new_avatar_url):
        # Atualiza perfil na sessão
        st.session_state.user_profile["avatar"] = new_avatar_url
        st.session_state.user_profile["avatar_config"] = st.session_state.avatar_config
        
        st.toast(f"Item {item['name']} equipado!", icon="👕")
        time.sleep(1)
        st.rerun()
    else:
        st.error("Erro ao equipar item.")

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
        
        # Opção de equipar imediatamente (via session state para persistir após rerun)
        st.session_state.just_bought = item['id']
        
        time.sleep(2)
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
                    # Preview do Avatar com o Item
                    preview_url = get_item_preview_url(item)
                    # Centralizar imagem
                    c_img1, c_img2, c_img3 = st.columns([1, 2, 1])
                    with c_img2:
                        st.image(preview_url, width=120)
                    
                    st.markdown(f"**{item['name']}**")
                    
                    # Verificar estado do item
                    is_owned = item['id'] in st.session_state.inventory
                    is_equipped = st.session_state.get("avatar_config", {}).get(cat_key) == item['id']
                    
                    if is_equipped:
                        st.button("✅ Equipado", key=f"eqd_{item['id']}", disabled=True, use_container_width=True)
                    elif is_owned:
                        if st.button("👕 Equipar", key=f"eq_{item['id']}", type="primary", use_container_width=True):
                            equip_item(item)
                    else:
                        st.markdown(f"**💰 {item['price']} XP**")
                        if st.button(f"Comprar", key=f"buy_{item['category']}_{item['id']}", use_container_width=True):
                            buy_item(item)

# --- CONSUMÍVEIS (ENERGIA) ---
st.markdown("### ⚡ Energia & Consumíveis")

col_energy1, col_energy2 = st.columns([1, 2])

with col_energy1:
    with st.container(border=True):
        st.markdown("<div style='text-align: center; font-size: 40px;'>🔋</div>", unsafe_allow_html=True)
        st.markdown("<h4 style='text-align: center;'>Bateria Extra</h4>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; font-size: 12px;'>Recupera 1 energia</p>", unsafe_allow_html=True)
        
        # Logic for daily limit
        from datetime import datetime
        today_str = datetime.now().strftime("%Y-%m-%d")
        
        if "daily_energy_purchases" not in st.session_state.user_profile or st.session_state.user_profile["daily_energy_purchases"].get("date") != today_str:
            st.session_state.user_profile["daily_energy_purchases"] = {"date": today_str, "count": 0}
            
        purchased_count = st.session_state.user_profile["daily_energy_purchases"]["count"]
        LIMIT = 10
        PRICE = 50
        
        st.markdown(f"<p style='text-align: center; font-weight: bold;'>💰 {PRICE} XP</p>", unsafe_allow_html=True)
        st.progress(purchased_count / LIMIT, text=f"Hoje: {purchased_count}/{LIMIT}")
        
        btn_disabled = purchased_count >= LIMIT or st.session_state.xp < PRICE
        
        if st.button("Comprar Energia", disabled=btn_disabled, use_container_width=True):
            st.session_state.xp -= PRICE
            st.session_state.neural_battery = min(st.session_state.neural_battery + 1, 10) # Cap at 10? User said "max 10 energias por dia" exchange, usually max capacity is 10 too.
            # Increment count
            st.session_state.user_profile["daily_energy_purchases"]["count"] += 1
            
            save_user_progress()
            st.toast("Energia recarregada! ⚡", icon="🔋")
            st.rerun()

st.markdown("---")
st.info("💡 Dica: O preview mostra como o item ficará no seu avatar atual!")
