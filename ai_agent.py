import os
import google.generativeai as genai
from dotenv import load_dotenv
import json
import re

# Load environment variables
load_dotenv()

class MathAI:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in .env file")
        
        genai.configure(api_key=api_key)
        
        # Primary model
        self.primary_model_name = 'gemini-2.5-flash-lite'
        self.fallback_model_name = 'gemini-2.0-flash-lite'
        
        # Start with primary model
        self.model = genai.GenerativeModel(
            self.primary_model_name,
            generation_config={
                "temperature": 0.7,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 1024,
            }
        )
        self.current_model_name = self.primary_model_name
        self.use_fallback = False
        self.prepayment_depleted = False
    
    def _generate_with_fallback(self, prompt):
        """
        Tenta gerar conteúdo com o modelo primário, 
        se falhar por rate limit, usa o modelo fallback automaticamente.
        """
        try:
            response = self.model.generate_content(prompt)
            return response
        except Exception as e:
            error_str = str(e).lower()
            
            # Check if prepayment is depleted
            if 'prepayment' in error_str or 'depleted' in error_str:
                self.prepayment_depleted = True
            
            # Check if it's a rate limit error OR a 404/Not Found (model not available)
            if 'rate' in error_str or 'quota' in error_str or 'limit' in error_str or '429' in error_str or 'not found' in error_str or '404' in error_str:
                print(f"[WARN] Erro no modelo {self.current_model_name}: {e}")
                
                # Switch to fallback model if not already using it
                if not self.use_fallback:
                    print(f"[INFO] Trocando automaticamente para {self.fallback_model_name}")
                    self.model = genai.GenerativeModel(
                        self.fallback_model_name,
                        generation_config={
                            "temperature": 0.7,
                            "top_p": 0.95,
                            "top_k": 40,
                            "max_output_tokens": 1024,
                        }
                    )
                    self.current_model_name = self.fallback_model_name
                    self.use_fallback = True
                    
                    # Try again with fallback model
                    try:
                        response = self.model.generate_content(prompt)
                        print(f"[SUCCESS] Sucesso com {self.fallback_model_name}")
                        return response
                    except Exception as fallback_error:
                        fallback_error_str = str(fallback_error).lower()
                        if 'prepayment' in fallback_error_str or 'depleted' in fallback_error_str:
                            self.prepayment_depleted = True
                        print(f"[ERROR] Erro também no fallback: {fallback_error}")
                        raise fallback_error
                else:
                    # Already using fallback, re-raise the error
                    raise e
            else:
                # Not a rate limit error, re-raise
                raise e
    
    def get_completed_bncc_skills_summary(self, completed_skills_dict):
        """
        Gera um resumo das habilidades BNCC já desenvolvidas para contexto da IA.
        """
        if not completed_skills_dict:
            return "Nenhuma habilidade desenvolvida ainda."
        
        skills_list = []
        for mission_id, bncc_data in completed_skills_dict.items():
            skill_code = bncc_data.get('habilidade', 'N/A')
            skills_list.append(skill_code)
        
        return ", ".join(skills_list[:5])  # Limit to 5 skills

    def generate_methodology(self, profile_data):
        """
        Generates a teaching methodology based on the student's profile.
        """
        prompt = f"""Analise o perfil e sugira uma metodologia de ensino em JSON:
Perfil: Nome={profile_data.get('name')}, Idade={profile_data.get('age')}, Confiança={profile_data.get('confidence')}/10, Interesses={profile_data.get('interest')}

JSON (sem markdown):
{{"methodology": "Nome da Metodologia", "description": "Breve explicação (1 frase)"}}"""
        
        try:
            response = self._generate_with_fallback(prompt)
            return json.loads(self._clean_json(response.text))
        except Exception as e:
            print(f"Error generating methodology: {e}")
            return {"methodology": "Gamificação", "description": "Aprendizado através de desafios e recompensas."}

    def generate_missions(self, methodology, level, interests, completed_bncc_skills=None):
        """
        Generates 3 gamified math missions based on methodology and interests.
        Aligns challenges to the Flow Channel to sustain engagement.
        """
        skills_note = ""
        if completed_bncc_skills:
            skills_summary = self.get_completed_bncc_skills_summary(completed_bncc_skills)
            skills_note = f"Evite repetir habilidades já desenvolvidas: {skills_summary}"
        
        prompt = f"""Você é o motor de Gamificação Adaptativa do ecossistema MATEMAI.
Sua missão é criar 3 missões de matemática para Nível {level} alinhadas às diretrizes da BNCC (Base Nacional Comum Curricular).

Regras importantes:
1. Adapte as missões à metodologia "{methodology}" e aos interesses do aluno: "{interests}".
2. Crie uma narrativa envolvente e lúdica para cada missão.
3. Garanta uma progressão de dificuldade gradual que mantenha o aluno no Canal de Fluxo (Flow), evitando ansiedade (desafio complexo demais) ou tédio (desafio simples demais).
{skills_note}

Gere o output estritamente no seguinte formato JSON (sem markdown):
[
  {{"id": 1, "title": "Título criativo e contextualizado", "desc": "Objetivo lúdico da missão", "xp": 100, "status": "unlocked"}},
  {{"id": 2, "title": "Título criativo e contextualizado", "desc": "Objetivo lúdico da missão", "xp": 150, "status": "locked"}},
  {{"id": 3, "title": "Título criativo e contextualizado", "desc": "Objetivo lúdico da missão", "xp": 200, "status": "locked"}}
]"""
        
        try:
            response = self._generate_with_fallback(prompt)
            return json.loads(self._clean_json(response.text))
        except Exception as e:
            print(f"Error generating missions: {e}")
            return []

    def generate_greeting(self, name):
        """
        Generates a warm, personalized greeting for the student.
        """
        prompt = f"Escreva uma saudação curta, motivadora e acolhedora para {name}. Use emojis. Máximo 2 frases."
        
        try:
            response = self._generate_with_fallback(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Error generating greeting: {e}")
            return f"Olá, {name}! Pronto para uma aventura matemática? 🚀"

    def generate_problem(self, mission_title, mission_desc, level):
        """
        Generates a math problem using internal Chain-of-Thought validation.
        """
        prompt = f"""Você é o tutor inteligente do ecossistema MATEMAI.
Sua tarefa é criar um problema matemático CURTO de Nível {level} alinhado à BNCC, baseado no contexto da missão e personalizado semanticamente com os interesses do aluno.

Regras importantes:
1. Use a técnica Chain-of-Thought (Cadeia de Pensamento) para resolver o problema passo a passo internamente antes de gerar o enunciado final.
2. Certifique-se de que a resposta numérica/curta exata esteja absolutamente correta.
3. Crie uma dica sutil baseada em mediação socrática (andaime cognitivo/scaffolding) que ajude o aluno sem revelar a resposta diretamente.

Contexto da Missão: {mission_title} - {mission_desc}

Gere a resposta estritamente no seguinte formato JSON (sem markdown):
{{
  "chain_of_thought": "Resolução passo a passo detalhada e validação interna do problema",
  "question": "O enunciado do problema, contextualizado e amigável para o aluno",
  "hint": "Uma dica socrática de scaffolding que estimule o raciocínio sem dar a resposta direta",
  "solution": "A resposta exata (número ou palavra muito curta)"
}}"""
        
        try:
            response = self._generate_with_fallback(prompt)
            return json.loads(self._clean_json(response.text))
        except Exception as e:
            print(f"Error generating problem: {e}")
            return {"question": "Quanto é 2 + 2?", "hint": "Conte nos dedos!", "solution": "4"}

    def get_bncc_alignment(self, mission_title, mission_desc, school_year, level):
        """
        Identifica a competência e habilidade da BNCC sendo trabalhada na missão.
        """
        prompt = f"""Identifique a competência e habilidade BNCC de Matemática.
Missão: {mission_title}
Ano/Série: {school_year}

Gere a resposta estritamente no seguinte formato JSON (sem markdown):
{{"competencia": "Competência X", "competencia_texto": "Texto da Competência", "habilidade": "EFXXMAXX", "habilidade_texto": "Descrição oficial da habilidade"}}"""
        
        try:
            response = self._generate_with_fallback(prompt)
            return json.loads(self._clean_json(response.text))
        except Exception as e:
            print(f"Error getting BNCC alignment: {e}")
            return {
                "competencia": "Competência 1",
                "competencia_texto": "Reconhecer que a Matemática é uma ciência humana.",
                "habilidade": "EF06MA01",
                "habilidade_texto": "Comparar e ordenar números naturais."
            }

    def validate_answer(self, question, user_answer, attempt_number=1, expected_answer=None):
        """
        Validates the student's answer using socratic mediation, diagnostic feedback, and scaffolding.
        """
        truth_context = f"RESPOSTA CORRETA ESPERADA: {expected_answer}" if expected_answer else ""
        
        prompt = f"""Você é o Agente Socrático do ecossistema MATEMAI, atuando como o "Par Mais Capaz" na Zona de Desenvolvimento Proximal (ZDP) do aluno.
Sua missão é validar a resposta do aluno para o desafio de matemática abaixo.

PRINCÍPIO PEDAGÓGICO INVIOLÁVEL: Você está terminantemente PROIBIDO de fornecer a resposta direta ({expected_answer}) ao estudante. Em vez disso, guie-o socraticamente para que ele descubra a resposta por si mesmo através de andaimes cognitivos (scaffolding).

Pergunta: {question}
Resposta do Aluno: {user_answer}
{truth_context}
Número da Tentativa atual: {attempt_number}

Analise detalhadamente a resposta do aluno:
1. Se a resposta estiver CORRETA:
   - Defina "correct" como true.
   - No "feedback", dê parabéns calorosos e motivadores, contextualizando e reforçando brevemente o conceito matemático por trás da resolução correta.

2. Se a resposta estiver INCORRETA:
   - Defina "correct" como false.
   - Faça uma ANÁLISE DIAGNÓSTICA DO ERRO: identifique se o erro é PROCEDIMENTAL (erro de cálculo simples/desatenção) ou CONCEITUAL (dificuldade profunda em entender a regra/fórmula).
   - No "feedback", ofereça um andaime cognitivo (scaffolding/dica socrática) personalizado. Use metáforas ou analogias baseadas em temas juvenis (como música, jogos, etc.). Estimule-o a tentar novamente, tratando a nova tentativa como um "Respawn" (oportunidade de recomeço e aprendizado, não punição).
   - NUNCA mostre a resposta final ({expected_answer}). Diga apenas que ele está no caminho ou dê uma pista do próximo passo.

Gere a resposta estritamente no seguinte formato JSON (sem markdown):
{{
  "correct": true/false,
  "error_type": "conceitual" ou "procedimental" ou "nenhum",
  "feedback": "Seu feedback socrático e motivador formatado com markdown"
}}"""
        
        try:
            response = self._generate_with_fallback(prompt)
            response_text = response.text.strip()
            
            # Try to parse JSON
            try:
                result = json.loads(self._clean_json(response_text))
                if "correct" in result and "feedback" in result:
                    return result
            except json.JSONDecodeError:
                pass
            
            # Fallback: analyze text
            response_lower = response_text.lower()
            correct_indicators = ["correto", "certo", "parabéns", "excelente", "perfeito", "acertou"]
            is_correct = any(ind in response_lower for ind in correct_indicators)
            
            if is_correct:
                # Use the generated text as feedback if it seems reasonable, otherwise fallback
                feedback = response_text if len(response_text) > 10 else "Parabéns! Resposta correta! 🎉"
                return {"correct": True, "feedback": feedback}
            else:
                return {"correct": False, "feedback": response_text}
                
        except Exception as e:
            print(f"Error validating answer: {e}")
            
            # Deterministic fallback: Compare with expected_answer if available
            if expected_answer:
                try:
                    # Normalize strings for comparison (remove spaces, lowercase, handle decimal points)
                    def normalize(s):
                        if not s: return ""
                        s = str(s).strip().lower().replace(" ", "")
                        s = s.replace(",", ".") # Handle decimal separator
                        return s
                    
                    norm_user = normalize(user_answer)
                    norm_expected = normalize(expected_answer)
                    
                    if norm_user == norm_expected:
                        return {"correct": True, "feedback": "Resposta correta! (Validação automática) 🎉"}
                    
                    # Also try to check if expected answer is contained in user answer (for sentence answers)
                    if len(norm_expected) > 3 and norm_expected in norm_user:
                         return {"correct": True, "feedback": "Resposta correta! (Validação automática) 🎉"}
                         
                except Exception as fallback_e:
                    print(f"Error in deterministic fallback: {fallback_e}")
            
            return {"correct": False, "feedback": "Erro ao validar. Tente novamente."}

    def generate_next_mission(self, last_mission_title, methodology, level, interests):
        """
        Generates the next mission in the sequence, increasing difficulty.
        """
        xp = 100 + (level * 50)
        prompt = f"""Você é o motor de Gamificação Adaptativa do MATEMAI.
Gere a próxima missão de matemática de Nível {level} na sequência da trilha de aprendizagem.

Regras importantes:
1. Garanta que a missão esteja no Canal de Fluxo (Flow Channel): aumente o desafio de forma sutil em relação à missão anterior "{last_mission_title}" para evitar ansiedade ou tédio.
2. Use a metodologia "{methodology}" e os interesses do aluno: "{interests}" para criar um título e descrição com forte engajamento narrativo.
3. Alinhe a missão a uma habilidade da BNCC (Base Nacional Comum Curricular).

Gere o output estritamente no seguinte formato JSON (sem markdown):
{{
  "title": "Título criativo e motivador",
  "desc": "Descrição envolvente com o objetivo pedagógico em linguagem lúdica",
  "xp": {xp},
  "status": "locked"
}}"""
        
        try:
            response = self._generate_with_fallback(prompt)
            return json.loads(self._clean_json(response.text))
        except Exception as e:
            print(f"Error generating next mission: {e}")
            return {"title": "Nova Aventura", "desc": "Continue sua jornada!", "xp": xp, "status": "locked"}

    def _clean_json(self, text):
        """Helper to clean markdown code blocks from JSON response"""
        # Remove markdown code blocks
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        
        text = text.strip()
        
        # Try to find JSON object or array
        json_match = re.search(r'(\{.*\}|\[.*\])', text, re.DOTALL)
        if json_match:
            return json_match.group(1)
            
        return text
