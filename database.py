import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import streamlit as st
import os

class FirestoreDB:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FirestoreDB, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        try:
            # Tenta inicializar com credenciais do arquivo
            cred_path = "firebase-credentials.json"
            
            if not os.path.exists(cred_path):
                st.error("⚠️ Arquivo firebase-credentials.json não encontrado!")
                st.info("Por favor, siga as instruções no guia de configuração.")
                self.db = None
                return
            
            # Inicializa Firebase apenas uma vez
            if not firebase_admin._apps:
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
            
            self.db = firestore.client()
            self._initialized = True
            
        except Exception as e:
            st.error(f"Erro ao conectar ao Firestore: {e}")
            self.db = None
    
    def save_user(self, email, name, avatar, nickname=None):
        """Salva informações básicas do usuário"""
        if not self.db:
            return False
            
        try:
            user_ref = self.db.collection('users').document(email)
            user_data = {
                'email': email,
                'name': name,
                'avatar': avatar,
                'created_at': datetime.now(),
                'last_login': datetime.now()
            }
            if nickname:
                user_data['nickname'] = nickname
                
            user_ref.set(user_data, merge=True)
            return True
        except Exception as e:
            st.error(f"Erro ao salvar usuário: {e}")
            return False
    
    def get_user(self, email):
        """Recupera informações básicas do usuário"""
        if not self.db:
            return None
            
        try:
            doc = self.db.collection('users').document(email).get()
            if doc.exists:
                return doc.to_dict()
            return None
        except Exception as e:
            st.error(f"Erro ao buscar usuário: {e}")
            return None

    def save_progress(self, email, xp, level, profile_data, missions_data, **kwargs):
        """Salva o progresso completo do usuário"""
        if not self.db:
            return False
            
        try:
            # Ensure keys are strings for Firestore
            completed_bncc_skills = kwargs.get('completed_bncc_skills', {})
            completed_bncc_skills = {str(k): v for k, v in completed_bncc_skills.items()}

            progress_ref = self.db.collection('progress').document(email)
            progress_ref.set({
                'xp': xp,
                'level': level,
                'profile_data': profile_data,
                'missions_data': missions_data,
                'exercises_completed_count': kwargs.get('exercises_completed_count', 0),
                'current_streak': kwargs.get('current_streak', 0),
                # Study Schedule Data
                'study_days': kwargs.get('study_days', {}),
                'current_study_streak': kwargs.get('current_study_streak', 0),
                # Daily Missions Data
                'daily_missions': kwargs.get('daily_missions', {}),
                'daily_missions_xp': kwargs.get('daily_missions_xp', {}),
                'daily_mission_progress': kwargs.get('daily_mission_progress', {}),
                # BNCC Skills Data
                'completed_bncc_skills': completed_bncc_skills,
                # Neural Battery
                'neural_battery': kwargs.get('neural_battery', 10),
                'last_battery_reset': kwargs.get('last_battery_reset', datetime.now().strftime("%Y-%m-%d")),
                'updated_at': datetime.now()
            })
            return True
        except Exception as e:
            st.error(f"Erro ao salvar progresso: {e}")
            return False
    
    def load_progress(self, email):
        """Carrega o progresso do usuário"""
        if not self.db:
            return None
            
        try:
            progress_ref = self.db.collection('progress').document(email)
            doc = progress_ref.get()
            
            if doc.exists:
                data = doc.to_dict()
                return {
                    'xp': data.get('xp', 0),
                    'level': data.get('level', 1),
                    'profile': data.get('profile_data', {}),
                    'missions': data.get('missions_data', []),
                    'exercises_completed_count': data.get('exercises_completed_count', 0),
                    'current_streak': data.get('current_streak', 0),
                    # Study Schedule Data
                    'study_days': data.get('study_days', {}),
                    'current_study_streak': data.get('current_study_streak', 0),
                    # Daily Missions Data
                    'daily_missions': data.get('daily_missions', {}),
                    'daily_missions_xp': data.get('daily_missions_xp', {}),
                    'daily_mission_progress': data.get('daily_mission_progress', {}),
                    # BNCC Skills Data
                    'daily_mission_progress': data.get('daily_mission_progress', {}),
                    # BNCC Skills Data
                    'completed_bncc_skills': data.get('completed_bncc_skills', {}),
                    # Neural Battery
                    'neural_battery': data.get('neural_battery', 10),
                    'last_battery_reset': data.get('last_battery_reset', datetime.now().strftime("%Y-%m-%d")),
                    # Avatar Config
                    'avatar_config': data.get('avatar_config', {})
                }
            return None
        except Exception as e:
            st.error(f"Erro ao carregar progresso: {e}")
            return None
    
    def update_last_login(self, email):
        """Atualiza o último login do usuário"""
        if not self.db:
            return
            
        try:
            user_ref = self.db.collection('users').document(email)
            user_ref.update({'last_login': datetime.now()})
        except Exception as e:
            print(f"Erro ao atualizar último login: {e}")
    
    def get_user_stats(self, email):
        """Retorna estatísticas do usuário"""
        if not self.db:
            return None
            
        try:
            progress = self.load_progress(email)
            if progress:
                completed_missions = [m for m in progress['missions'] if m.get('status') == 'completed']
                return {
                    'total_xp': progress['xp'],
                    'level': progress['level'],
                    'missions_completed': len(completed_missions),
                    'total_missions': len(progress['missions'])
                }
            return None
            return None
        except Exception as e:
            print(f"Erro ao obter estatísticas: {e}")
            return None

    def reset_progress(self, email):
        """Reseta o progresso do usuário (apaga documento de progresso)"""
        if not self.db:
            return False
            
        try:
            self.db.collection('progress').document(email).delete()
            return True
        except Exception as e:
            st.error(f"Erro ao resetar progresso: {e}")
            return False

    def get_leaderboard(self, limit=10):
        """Retorna o ranking dos usuários ordenado por XP"""
        if not self.db:
            return []
            
        try:
            # Query progress collection ordered by xp descending
            docs = self.db.collection('progress').order_by('xp', direction=firestore.Query.DESCENDING).limit(limit).stream()
            
            leaderboard = []
            for doc in docs:
                data = doc.to_dict()
                profile = data.get('profile_data', {})
                
                leaderboard.append({
                    'name': profile.get('name', 'Usuário Anônimo'),
                    'nickname': profile.get('nickname', None), # Get nickname
                    'school': profile.get('school_name', 'Escola Não Informada'),
                    'xp': data.get('xp', 0),
                    'level': data.get('level', 1),
                    'avatar': profile.get('avatar', 'assets/mascot.png'), # Fallback avatar
                    'id': doc.id # Email/ID for identification
                })
            
            return leaderboard
        except Exception as e:
            print(f"Erro ao obter ranking: {e}")
            return []

    def get_user_rank(self, email, current_xp):
        """Retorna a posição do usuário no ranking"""
        if not self.db:
            return "-"
            
        try:
            # Count users with more XP
            # Note: Firestore count queries are efficient
            query = self.db.collection('progress').where(filter=firestore.FieldFilter('xp', '>', current_xp))
            count_query = query.count()
            results = count_query.get()
            
            # Rank is count + 1
            return results[0][0].value + 1
        except Exception as e:
            print(f"Erro ao obter rank do usuário: {e}")
            return "-"

    def save_order(self, email, order_data):
        """Salva um pedido de troca de XP"""
        if not self.db:
            return False
            
        try:
            # Adiciona timestamp se não existir
            if 'created_at' not in order_data:
                order_data['created_at'] = datetime.now()
            
            # Salva na subcoleção 'orders' do usuário
            self.db.collection('users').document(email).collection('orders').add(order_data)
            return True
        except Exception as e:
            st.error(f"Erro ao salvar pedido: {e}")
            return False

    def save_avatar_config(self, email, avatar_config, avatar_url):
        """Salva a configuração do avatar do usuário"""
        if not self.db:
            return False
            
        try:
            # Atualizar URL do avatar no perfil do usuário
            self.db.collection('users').document(email).update({'avatar': avatar_url})
            
            # Salvar configuração detalhada no progresso
            self.db.collection('progress').document(email).update({
                'avatar_config': avatar_config,
                'profile_data.avatar': avatar_url # Update nested profile data too
            })
            return True
        except Exception as e:
            st.error(f"Erro ao salvar avatar: {e}")
            return False

    def get_all_users(self):
        """Retorna uma lista com todos os usuários e seus progressos (Admin)"""
        if not self.db:
            return []
            
        try:
            # Buscar todos os usuários
            users_ref = self.db.collection('users')
            users_docs = users_ref.stream()
            
            all_users = []
            for doc in users_docs:
                user_data = doc.to_dict()
                email = user_data.get('email')
                
                # Buscar progresso correspondente
                progress_data = self.load_progress(email)
                
                user_info = {
                    'email': email,
                    'name': user_data.get('name', 'N/A'),
                    'nickname': user_data.get('nickname', 'N/A'),
                    'last_login': user_data.get('last_login'),
                    'created_at': user_data.get('created_at'),
                    'xp': progress_data.get('xp', 0) if progress_data else 0,
                    'level': progress_data.get('level', 1) if progress_data else 1,
                    'school': progress_data.get('profile', {}).get('school_name', 'N/A') if progress_data else 'N/A'
                }
                all_users.append(user_info)
                
            return all_users
        except Exception as e:
            st.error(f"Erro ao buscar usuários: {e}")
            return []

    def delete_user(self, email):
        """Deleta um usuário e seus dados associados (Admin)"""
        if not self.db:
            return False
            
        try:
            # Deletar documento de usuário
            self.db.collection('users').document(email).delete()
            
            # Deletar documento de progresso
            self.db.collection('progress').document(email).delete()
            
            # Deletar subcoleção de pedidos (opcional, mas recomendado limpar)
            # Firestore não deleta subcoleções automaticamente, teria que iterar.
            # Para simplificar, assumimos que o principal é o user e progress.
            
            return True
        except Exception as e:
            st.error(f"Erro ao deletar usuário: {e}")
            return False

    def update_user_admin(self, email, update_data):
        """Atualiza dados do usuário via admin"""
        if not self.db:
            return False
            
        try:
            # Separar dados de usuário e progresso
            user_fields = ['name', 'nickname']
            progress_fields = ['xp', 'level']
            
            user_update = {k: v for k, v in update_data.items() if k in user_fields}
            
            # Atualizar collection users
            if user_update:
                self.db.collection('users').document(email).update(user_update)
            
            # Atualizar collection progress
            # Precisamos carregar o progresso atual para atualizar campos aninhados se necessário,
            # mas aqui vamos simplificar atualizando campos de topo do documento progress
            progress_update = {}
            if 'xp' in update_data:
                progress_update['xp'] = update_data['xp']
            if 'level' in update_data:
                progress_update['level'] = update_data['level']
                
            if progress_update:
                # Verificar se documento existe antes de update
                progress_ref = self.db.collection('progress').document(email)
                if progress_ref.get().exists:
                    progress_ref.update(progress_update)
                
            return True
        except Exception as e:
            st.error(f"Erro ao atualizar usuário: {e}")
            return False

# Singleton instance
@st.cache_resource
def get_database():
    """Retorna a instância única do banco de dados"""
    return FirestoreDB()
