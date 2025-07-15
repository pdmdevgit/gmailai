from openai import OpenAI
import anthropic
import json
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import re

logger = logging.getLogger(__name__)

class AIService:
    """Service for AI-powered email classification and response generation"""
    
    def __init__(self, openai_api_key: str = None, anthropic_api_key: str = None, model: str = 'gpt-4'):
        self.openai_client = None
        self.anthropic_client = None
        self.model = model
        
        if openai_api_key:
            self.openai_client = OpenAI(api_key=openai_api_key)
        
        if anthropic_api_key:
            self.anthropic_client = anthropic.Anthropic(api_key=anthropic_api_key)
    
    def classify_email(self, email_data: Dict) -> Dict:
        """Classify email by type, priority, product interest, and sentiment"""
        try:
            classification_prompt = self._build_classification_prompt(email_data)
            
            if self.model.startswith('gpt') and self.openai_client:
                response = self._classify_with_openai(classification_prompt)
            elif self.model.startswith('claude') and self.anthropic_client:
                response = self._classify_with_anthropic(classification_prompt)
            else:
                raise ValueError("No valid AI client configured")
            
            classification = self._parse_classification_response(response)
            
            logger.info(f"Email classified: {classification}")
            return classification
            
        except Exception as e:
            logger.error(f"Error classifying email: {str(e)}")
            return self._get_default_classification()
    
    def generate_response(self, email_data: Dict, classification: Dict, template: Dict = None) -> Dict:
        """Generate AI response for email"""
        try:
            response_prompt = self._build_response_prompt(email_data, classification, template)
            
            if self.model.startswith('gpt') and self.openai_client:
                response = self._generate_with_openai(response_prompt)
            elif self.model.startswith('claude') and self.anthropic_client:
                response = self._generate_with_anthropic(response_prompt)
            else:
                raise ValueError("No valid AI client configured")
            
            generated_response = self._parse_response_generation(response)
            
            logger.info(f"Response generated for email {email_data.get('gmail_id', 'unknown')}")
            return generated_response
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return self._get_default_response()
    
    def _build_classification_prompt(self, email_data: Dict) -> str:
        """Build prompt for email classification"""
        sender = email_data.get('sender_name', '') or email_data.get('sender_email', '')
        subject = email_data.get('subject', '')
        body = email_data.get('body_text', '')[:2000]  # Limit body length
        
        prompt = f"""
Você é um especialista em classificação de emails para o negócio do Prof. Diogo Moreira, especialista em preparação para concursos públicos fiscais.

CONTEXTO DO NEGÓCIO:
- Especialista em concursos fiscais (SEFAZ, Receita Federal, TCE, TRF)
- Produtos: Coaching Individual (R$ 2.997) e Acelerador (R$ 497)
- Metodologia dos 9 passos para aprovação em 9 meses
- Cases de sucesso: Vitória Barbosa (SEFAZ-BA), Thales (múltiplas aprovações)

EMAIL PARA CLASSIFICAR:
Remetente: {sender}
Assunto: {subject}
Conteúdo: {body}

CLASSIFIQUE o email nas seguintes categorias:

1. TIPO (escolha 1):
   - vendas: interesse em produtos, orçamentos, informações comerciais
   - suporte: dúvidas técnicas, problemas, reclamações
   - informacao: pedidos de informação geral, metodologia, dúvidas sobre concursos
   - spam: emails irrelevantes, promocionais não relacionados
   - agendamento: pedidos para marcar reuniões, calls, consultorias

2. PRIORIDADE (escolha 1):
   - alta: interesse direto em compra, problemas urgentes, leads quentes
   - media: dúvidas gerais, interesse moderado
   - baixa: informações básicas, curiosidade inicial

3. PRODUTO DE INTERESSE (escolha 1 ou none):
   - coaching: interesse em mentoria individual
   - acelerador: interesse no curso metodologia
   - none: não demonstra interesse específico

4. SENTIMENTO (escolha 1):
   - positivo: entusiasmado, motivado, interessado
   - neutro: neutro, informativo
   - negativo: frustrado, reclamação, descontente

5. CONFIANÇA (0.0 a 1.0): sua confiança na classificação

Responda APENAS em formato JSON:
{{
    "type": "vendas|suporte|informacao|spam|agendamento",
    "priority": "alta|media|baixa", 
    "product": "coaching|acelerador|none",
    "sentiment": "positivo|neutro|negativo",
    "confidence": 0.85,
    "reasoning": "breve explicação da classificação"
}}
"""
        return prompt
    
    def _build_response_prompt(self, email_data: Dict, classification: Dict, template: Dict = None) -> str:
        """Build prompt for response generation"""
        sender_name = email_data.get('sender_name', '') or 'Amigo(a)'
        sender_email = email_data.get('sender_email', '')
        subject = email_data.get('subject', '')
        body = email_data.get('body_text', '')[:2000]
        
        # Extract first name
        first_name = sender_name.split()[0] if sender_name else 'Amigo(a)'
        
        template_guidance = ""
        if template:
            template_guidance = f"""
TEMPLATE BASE:
Assunto: {template.get('subject_template', '')}
Corpo: {template.get('body_template', '')}
"""
        
        prompt = f"""
Você é o Prof. Diogo Moreira, especialista em preparação para concursos públicos fiscais.

SEU PERFIL:
- Aprovado em concursos fiscais de alto nível
- Criador da metodologia dos 9 passos
- Especialista em SEFAZ, Receita Federal, TCE, TRF
- Tom: profissional, empático, motivador, direto
- Foco: transformação de vida através da aprovação

PRODUTOS:
- Coaching Individual (R$ 1.497): mentoria personalizada semanal
- Acelerador (R$ 497): curso com metodologia dos 9 passos

CASES DE SUCESSO:
- Vitória Barbosa: aprovada SEFAZ-BA
- Thales: aprovado TCE-RS, MPU, TRF-3, TRF-4, TRE-PA

EMAIL RECEBIDO:
De: {sender_name} <{sender_email}>
Assunto: {subject}
Conteúdo: {body}

CLASSIFICAÇÃO: {classification}

{template_guidance}

INSTRUÇÕES PARA RESPOSTA:
1. Use o nome "{first_name}" para personalizar
2. Responda de forma direta e prática
3. Inclua elementos motivacionais baseados em resultados
4. Se for interesse comercial, inclua call-to-action claro
5. Mantenha tom profissional mas acessível
6. Use dados concretos (9 meses vs 3-5 anos da média)
7. Mencione cases de sucesso quando relevante

ESTRUTURA:
- Cumprimento personalizado
- Resposta direta à questão
- Informações relevantes sobre metodologia/produtos
- Call-to-action específico
- Assinatura profissional

Gere uma resposta completa em formato JSON:
{{
    "subject": "assunto da resposta",
    "body_text": "corpo da resposta em texto",
    "body_html": "corpo da resposta em HTML (opcional)",
    "confidence": 0.85,
    "template_used": "nome do template se aplicável",
    "call_to_action": "principal CTA da resposta"
}}
"""
        return prompt
    
    def _classify_with_openai(self, prompt: str) -> str:
        """Classify email using OpenAI"""
        response = self.openai_client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "Você é um especialista em classificação de emails para negócios de educação."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=500
        )
        return response.choices[0].message.content
    
    def _classify_with_anthropic(self, prompt: str) -> str:
        """Classify email using Anthropic Claude"""
        response = self.anthropic_client.messages.create(
            model=self.model,
            max_tokens=500,
            temperature=0.1,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.content[0].text
    
    def _generate_with_openai(self, prompt: str) -> str:
        """Generate response using OpenAI"""
        response = self.openai_client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "Você é o Prof. Diogo Moreira, especialista em concursos fiscais."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1500
        )
        return response.choices[0].message.content
    
    def _generate_with_anthropic(self, prompt: str) -> str:
        """Generate response using Anthropic Claude"""
        response = self.anthropic_client.messages.create(
            model=self.model,
            max_tokens=1500,
            temperature=0.3,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.content[0].text
    
    def _parse_classification_response(self, response: str) -> Dict:
        """Parse AI classification response"""
        try:
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                classification = json.loads(json_str)
                
                # Validate and clean classification
                return {
                    'type': classification.get('type', 'informacao'),
                    'priority': classification.get('priority', 'media'),
                    'product': classification.get('product', 'none'),
                    'sentiment': classification.get('sentiment', 'neutro'),
                    'confidence': float(classification.get('confidence', 0.5)),
                    'reasoning': classification.get('reasoning', '')
                }
            else:
                return self._get_default_classification()
                
        except Exception as e:
            logger.error(f"Error parsing classification: {str(e)}")
            return self._get_default_classification()
    
    def _parse_response_generation(self, response: str) -> Dict:
        """Parse AI response generation"""
        try:
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                generated = json.loads(json_str)
                
                return {
                    'subject': generated.get('subject', 'Re: Sua consulta'),
                    'body_text': generated.get('body_text', ''),
                    'body_html': generated.get('body_html', ''),
                    'confidence': float(generated.get('confidence', 0.5)),
                    'template_used': generated.get('template_used', ''),
                    'call_to_action': generated.get('call_to_action', '')
                }
            else:
                return self._get_default_response()
                
        except Exception as e:
            logger.error(f"Error parsing response generation: {str(e)}")
            return self._get_default_response()
    
    def _get_default_classification(self) -> Dict:
        """Get default classification when AI fails"""
        return {
            'type': 'informacao',
            'priority': 'media',
            'product': 'none',
            'sentiment': 'neutro',
            'confidence': 0.0,
            'reasoning': 'Classificação automática falhou'
        }
    
    def _get_default_response(self) -> Dict:
        """Get default response when AI fails"""
        return {
            'subject': 'Re: Sua mensagem',
            'body_text': '''Olá,

Obrigado pelo seu contato!

Recebi sua mensagem e em breve retornarei com uma resposta personalizada.

Abraço,
Prof. Diogo Moreira''',
            'body_html': '',
            'confidence': 0.0,
            'template_used': 'default',
            'call_to_action': 'Aguardar resposta personalizada'
        }
    
    def analyze_email_intent(self, email_text: str) -> Dict:
        """Analyze specific intent and extract key information from email"""
        try:
            intent_prompt = f"""
Analise o seguinte email e extraia informações específicas sobre a intenção do remetente:

EMAIL: {email_text[:1500]}

Extraia e classifique:

1. INTENÇÃO PRINCIPAL:
   - comprar_agora: quer comprar imediatamente
   - solicitar_info: quer mais informações antes de decidir
   - agendar_conversa: quer falar por telefone/videochamada
   - comparar_opcoes: está comparando com outros cursos
   - duvida_tecnica: tem dúvidas específicas sobre metodologia
   - reclamacao: tem alguma reclamação ou problema

2. CONCURSO DE INTERESSE: qual concurso específico menciona (se houver)

3. EXPERIÊNCIA: iniciante, intermediário ou avançado nos estudos

4. URGÊNCIA: baixa, média ou alta (baseado na linguagem usada)

5. OBJEÇÕES APARENTES: preço, tempo, metodologia, credibilidade, etc.

Responda em JSON:
{{
    "intent": "intenção principal",
    "target_exam": "concurso específico ou 'não especificado'",
    "experience_level": "iniciante|intermediário|avançado",
    "urgency": "baixa|média|alta",
    "objections": ["lista", "de", "objeções"],
    "key_phrases": ["frases", "importantes", "do", "email"]
}}
"""
            
            if self.model.startswith('gpt') and self.openai_client:
                response = self.openai_client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": intent_prompt}],
                    temperature=0.1,
                    max_tokens=400
                )
                result = response.choices[0].message.content
            else:
                return {}
            
            # Parse JSON response
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            
            return {}
            
        except Exception as e:
            logger.error(f"Error analyzing email intent: {str(e)}")
            return {}
    
    def suggest_followup_actions(self, classification: Dict, intent_analysis: Dict) -> List[str]:
        """Suggest follow-up actions based on classification and intent"""
        actions = []
        
        # Based on classification type
        if classification.get('type') == 'vendas':
            if classification.get('priority') == 'alta':
                actions.append('Responder em até 1 hora')
                actions.append('Incluir depoimentos específicos')
                actions.append('Oferecer call de esclarecimento')
            
            if classification.get('product') == 'coaching':
                actions.append('Enviar material sobre coaching individual')
                actions.append('Destacar resultados personalizados')
            elif classification.get('product') == 'acelerador':
                actions.append('Enviar informações sobre metodologia')
                actions.append('Destacar custo-benefício')
        
        # Based on intent analysis
        intent = intent_analysis.get('intent', '')
        if intent == 'agendar_conversa':
            actions.append('Oferecer horários para call')
            actions.append('Enviar link do calendário')
        elif intent == 'comparar_opcoes':
            actions.append('Destacar diferenciais únicos')
            actions.append('Enviar comparativo de resultados')
        elif intent == 'duvida_tecnica':
            actions.append('Resposta técnica detalhada')
            actions.append('Incluir exemplos práticos')
        
        # Based on urgency
        if intent_analysis.get('urgency') == 'alta':
            actions.append('Priorizar resposta imediata')
            actions.append('Contato telefônico se necessário')
        
        return list(set(actions))  # Remove duplicates
    
    def generate_response_with_learning(self, email_data: Dict, classification: Dict, 
                                      learning_service=None, template: Dict = None) -> Dict:
        """
        Gera resposta usando aprendizado baseado no histórico de mensagens
        Esta é a funcionalidade principal que você perguntou!
        """
        try:
            account_name = email_data.get('account', '')
            
            # Contexto de aprendizado
            learning_context = {}
            similar_responses = []
            conversation_context = {}
            
            if learning_service:
                # Buscar respostas similares baseadas no histórico
                similar_responses = learning_service.find_similar_responses(
                    email_data.get('body_text', ''), account_name
                )
                
                # Analisar contexto da conversa se for thread
                thread_id = email_data.get('thread_id')
                if thread_id:
                    conversation_context = learning_service.get_conversation_context(
                        thread_id, account_name
                    )
                
                # Obter padrões de resposta aprendidos
                learning_context = learning_service.analyze_response_patterns(account_name)
            
            # Construir prompt enriquecido com aprendizado
            enhanced_prompt = self._build_learning_enhanced_prompt(
                email_data, classification, similar_responses, 
                conversation_context, learning_context, template
            )
            
            # Gerar resposta com contexto de aprendizado
            if self.model.startswith('gpt') and self.openai_client:
                response = self._generate_with_openai(enhanced_prompt)
            elif self.model.startswith('claude') and self.anthropic_client:
                response = self._generate_with_anthropic(enhanced_prompt)
            else:
                # Fallback para geração normal
                return self.generate_response(email_data, classification, template)
            
            generated_response = self._parse_response_generation(response)
            
            # Adicionar metadados de aprendizado
            generated_response['learning_applied'] = True
            generated_response['similar_responses_found'] = len(similar_responses)
            generated_response['conversation_stage'] = conversation_context.get('conversation_stage', 'unknown')
            
            logger.info(f"Response generated with learning for email {email_data.get('gmail_id', 'unknown')}")
            return generated_response
            
        except Exception as e:
            logger.error(f"Error generating response with learning: {str(e)}")
            # Fallback para geração normal
            return self.generate_response(email_data, classification, template)
    
    def _build_learning_enhanced_prompt(self, email_data: Dict, classification: Dict,
                                      similar_responses: List[Dict], conversation_context: Dict,
                                      learning_context: Dict, template: Dict = None) -> str:
        """
        Constrói prompt enriquecido com contexto de aprendizado do histórico
        """
        sender_name = email_data.get('sender_name', '') or 'Amigo(a)'
        sender_email = email_data.get('sender_email', '')
        subject = email_data.get('subject', '')
        body = email_data.get('body_text', '')[:2000]
        first_name = sender_name.split()[0] if sender_name else 'Amigo(a)'
        
        # Contexto de respostas similares
        similar_context = ""
        if similar_responses:
            similar_context = "\n\nRESPOSTAS SIMILARES DO SEU HISTÓRICO:\n"
            for i, resp in enumerate(similar_responses[:3], 1):
                similar_context += f"""
{i}. Assunto: {resp.get('subject', '')}
   Resposta: {resp.get('body_text', '')[:300]}...
   Similaridade: {resp.get('similarity_score', 0):.2f}
"""
        
        # Contexto da conversa
        conversation_info = ""
        if conversation_context:
            stage = conversation_context.get('conversation_stage', 'initial_contact')
            total_msgs = conversation_context.get('total_messages', 1)
            last_sentiment = conversation_context.get('sentiment_progression', [0])[-1] if conversation_context.get('sentiment_progression') else 0
            
            conversation_info = f"""
CONTEXTO DA CONVERSA:
- Estágio: {stage}
- Total de mensagens: {total_msgs}
- Último sentimento: {last_sentiment:.2f}
- Tópicos principais: {', '.join(conversation_context.get('key_topics', [])[:5])}
"""
        
        # Padrões aprendidos
        patterns_info = ""
        if learning_context:
            common_greetings = learning_context.get('greeting_patterns', [])[:3]
            common_closings = learning_context.get('closing_patterns', [])[:3]
            avg_length = learning_context.get('response_length_stats', {}).get('avg_length', 0)
            
            patterns_info = f"""
SEUS PADRÕES DE RESPOSTA APRENDIDOS:
- Saudações comuns: {', '.join(common_greetings)}
- Despedidas comuns: {', '.join(common_closings)}
- Comprimento médio das respostas: {avg_length:.0f} caracteres
- Total de respostas analisadas: {learning_context.get('total_analyzed', 0)}
"""
        
        # Template guidance
        template_guidance = ""
        if template:
            template_guidance = f"""
TEMPLATE BASE:
Assunto: {template.get('subject_template', '')}
Corpo: {template.get('body_template', '')}
"""
        
        prompt = f"""
Você é o Prof. Diogo Moreira, especialista em preparação para concursos públicos fiscais.

IMPORTANTE: Use seu HISTÓRICO DE RESPOSTAS para manter CONSISTÊNCIA no seu estilo e abordagem.

SEU PERFIL:
- Aprovado em concursos fiscais de alto nível
- Criador da metodologia dos 9 passos
- Especialista em SEFAZ, Receita Federal, TCE, TRF
- Tom: profissional, empático, motivador, direto
- Foco: transformação de vida através da aprovação

PRODUTOS:
- Coaching Individual (R$ 1.497): mentoria personalizada semanal
- Acelerador (R$ 497): curso com metodologia dos 9 passos

EMAIL ATUAL:
De: {sender_name} <{sender_email}>
Assunto: {subject}
Conteúdo: {body}

CLASSIFICAÇÃO: {classification}

{similar_context}

{conversation_info}

{patterns_info}

{template_guidance}

INSTRUÇÕES PARA RESPOSTA BASEADA NO SEU HISTÓRICO:
1. MANTENHA CONSISTÊNCIA com suas respostas anteriores similares
2. Use padrões de saudação e despedida que você já utiliza
3. Mantenha o comprimento de resposta similar ao seu padrão
4. Se há contexto de conversa, considere o histórico da thread
5. Adapte o tom baseado no estágio da conversa
6. Use frases e expressões que você já utilizou em contextos similares
7. Mantenha sua personalidade única e reconhecível

ESTRUTURA BASEADA NO SEU ESTILO:
- Saudação personalizada (baseada nos seus padrões)
- Resposta direta à questão (considerando respostas similares)
- Informações relevantes (consistente com seu histórico)
- Call-to-action específico (baseado no que funciona)
- Despedida profissional (usando seus padrões)

Gere uma resposta que seja CONSISTENTE com seu histórico mas PERSONALIZADA para este email específico:

{{
    "subject": "assunto da resposta",
    "body_text": "corpo da resposta em texto",
    "body_html": "corpo da resposta em HTML (opcional)",
    "confidence": 0.85,
    "template_used": "nome do template se aplicável",
    "call_to_action": "principal CTA da resposta",
    "learning_notes": "como o histórico influenciou esta resposta"
}}
"""
        return prompt
    
    def analyze_response_effectiveness(self, sent_response: Dict, follow_up_received: bool = False,
                                    response_time_hours: float = None) -> Dict:
        """
        Analisa a efetividade de uma resposta enviada
        Usado para melhorar o aprendizado contínuo
        """
        try:
            effectiveness = {
                'response_generated': True,
                'follow_up_received': follow_up_received,
                'response_time_hours': response_time_hours,
                'estimated_effectiveness': 0.5,  # Default
                'improvement_suggestions': []
            }
            
            # Analisar características da resposta
            body_text = sent_response.get('body_text', '')
            
            # Comprimento da resposta
            length = len(body_text)
            if length < 100:
                effectiveness['improvement_suggestions'].append('Resposta muito curta - considere mais detalhes')
                effectiveness['estimated_effectiveness'] -= 0.1
            elif length > 1000:
                effectiveness['improvement_suggestions'].append('Resposta muito longa - considere ser mais conciso')
                effectiveness['estimated_effectiveness'] -= 0.1
            else:
                effectiveness['estimated_effectiveness'] += 0.1
            
            # Presença de call-to-action
            cta = sent_response.get('call_to_action', '')
            if cta:
                effectiveness['estimated_effectiveness'] += 0.2
            else:
                effectiveness['improvement_suggestions'].append('Adicionar call-to-action claro')
            
            # Tempo de resposta
            if response_time_hours:
                if response_time_hours <= 2:
                    effectiveness['estimated_effectiveness'] += 0.2
                elif response_time_hours <= 24:
                    effectiveness['estimated_effectiveness'] += 0.1
                else:
                    effectiveness['improvement_suggestions'].append('Responder mais rapidamente')
            
            # Follow-up recebido é um bom sinal
            if follow_up_received:
                effectiveness['estimated_effectiveness'] += 0.3
            
            # Normalizar score
            effectiveness['estimated_effectiveness'] = max(0, min(1, effectiveness['estimated_effectiveness']))
            
            return effectiveness
            
        except Exception as e:
            logger.error(f"Error analyzing response effectiveness: {e}")
            return {'error': str(e)}
