import streamlit as st
from database import get_database
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
import os

# Configuration
# Ensure you have client_secret.json in the root directory
CLIENT_SECRETS_FILE = "client_secret.json"
SCOPES = [
    'openid', 
    'https://www.googleapis.com/auth/userinfo.email', 
    'https://www.googleapis.com/auth/userinfo.profile'
]
REDIRECT_URI = "http://localhost:8501"

def get_login_url():
    """
    Generates the Google OAuth authorization URL.
    """
    if not os.path.exists(CLIENT_SECRETS_FILE):
        return None

    try:
        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            CLIENT_SECRETS_FILE, scopes=SCOPES, redirect_uri=REDIRECT_URI
        )
        
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )
        return authorization_url
    except Exception as e:
        st.error(f"Erro ao gerar URL de login: {str(e)}")
        return None

def login_with_google():
    """
    Handles the Google Login flow using OAuth 2.0.
    """
    # 1. Check for OAuth Callback (Code in URL)
    if "code" in st.query_params:
        code = st.query_params["code"]
        
        try:
            # Create flow instance to exchange code for token
            flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
                CLIENT_SECRETS_FILE, scopes=SCOPES, redirect_uri=REDIRECT_URI
            )
            
            with st.spinner("🔐 Autenticando com Google..."):
                flow.fetch_token(code=code)
                credentials = flow.credentials
            
            with st.spinner("👤 Carregando informações do usuário..."):
                # 2. Get User Info from Google
                service = build('oauth2', 'v2', credentials=credentials)
                user_info = service.userinfo().get().execute()
                
                # Salvar informações básicas do usuário
                email = user_info.get("email")
                name = user_info.get("name", "Usuário")
                avatar = user_info.get("picture")
                
                st.session_state.user_profile = {
                    "name": name,
                    "email": email,
                    "avatar": avatar,
                }
                st.session_state.logged_in = True
            
            with st.spinner("💾 Salvando no banco de dados..."):
                # Salvar usuário no Firestore
                db = get_database()
                db.save_user(email, name, avatar)
                db.update_last_login(email)
            
            with st.spinner("📊 Carregando seu progresso..."):
                # Carregar progresso salvo
                from utils import load_user_progress
                load_user_progress(email)
            
            # Clean URL and Rerun
            st.query_params.clear()
            st.success(f"✅ Bem-vindo, {name}!")
            st.balloons()
            st.rerun()
            
        except Exception as e:
            error_msg = str(e)
            
            # Limpar URL para permitir nova tentativa
            st.query_params.clear()
            
            # Mensagem de erro mais amigável
            if "invalid_grant" in error_msg.lower():
                st.error("❌ O código de autenticação expirou!")
                st.info("💡 **Solução**: Clique no botão 'Entrar com Google' novamente abaixo.")
                st.warning("⏱️ Dica: Após clicar no botão do Google, complete o login rapidamente (em até 10 segundos).")
            else:
                st.error(f"❌ Erro durante o login: {error_msg}")
                st.info("Por favor, tente novamente clicando no botão abaixo.")
    
    # 2. Show Login Button (if not logged in and no code)
    else:
        url = get_login_url()
        if url:
            st.link_button("🇬 Entrar com Google", url, type="primary")
        else:
            st.error("Erro ao configurar login com Google.")

def logout():
    """Logs out the user"""
    # Salvar antes de sair
    with st.spinner("💾 Salvando seu progresso..."):
        from utils import save_user_progress
        save_user_progress()
    
    st.session_state.user_profile = None
    st.session_state.logged_in = False
    st.success("👋 Até logo!")
    st.rerun()

def check_authentication():
    """
    Checks if the user is logged in.
    Returns True if logged in, False otherwise.
    """
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    
    return st.session_state.logged_in
