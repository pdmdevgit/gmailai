import logging
import json
import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import Counter, defaultdict
import nltk
from textblob import TextBlob
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from .gmail_service import GmailService
from ..models import Email, ResponseTemplate

logger = logging.getLogger(__name__)

class LearningService:
    """
    Serviço de aprendizado baseado no histórico de mensagens
    Analisa padrões de resposta para melhorar a geração automática
    """
    
    def __init__(self, gmail_service: GmailService):
        self.gmail_service = gmail_service
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        
        # Baixar recursos NLTK necessários
        try:
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
        except:
            pass
    
    def analyze_response_patterns(self, account_name: str, days_back: int = 90) -> Dict:
        """
        Analisa padrões de resposta do histórico de emails enviados
        """
        logger.info(f"Analyzing response patterns for {account_name}")
        
        try:
            # Buscar histórico de emails enviados
            sent_emails = self.gmail_service.get_sent_emails_history(
                account_name, max_results=300, days_back=days_back
            )
            
            if not sent_emails:
                logger.warning(f"No sent emails found for {account_name}")
                return {}
            
            patterns = {
                'total_analyzed': len(sent_emails),
                'response_templates': self._extract_response_templates(sent_emails),
                'common_phrases': self._extract_common_phrases(sent_emails),
                'greeting_patterns': self._extract_greeting_patterns(sent_emails),
                'closing_patterns': self._extract_closing_patterns(sent_emails),
                'subject_patterns': self._extract_subject_patterns(sent_emails),
                'tone_analysis': self._analyze_tone_patterns(sent_emails),
                'response_length_stats': self._analyze_response_lengths(sent_emails),
                'keyword_frequency': self._extract_keyword_frequency(sent_emails)
            }
            
            logger.info(f"Successfully analyzed {len(sent_emails)} sent emails for {account_name}")
            return patterns
            
        except Exception as e:
            logger.error(f"Error analyzing response patterns: {e}")
            return {}
    
    def find_similar_responses(self, email_content: str, account_name: str, 
                             similarity_threshold: float = 0.3) -> List[Dict]:
        """
        Encontra respostas similares baseadas no conteúdo do email
        """
        try:
            # Extrair palavras-chave do email
            keywords = self._extract_keywords(email_content)
            
            # Buscar emails similares
            similar_emails = self.gmail_service.search_similar_emails(
                account_name, keywords, days_back=180
            )
            
            if not similar_emails:
                return []
            
            # Calcular similaridade usando TF-IDF
            email_texts = [email.get('body_text', '') for email in similar_emails]
            email_texts.append(email_content)
            
            try:
                tfidf_matrix = self.vectorizer.fit_transform(email_texts)
                similarities = cosine_similarity(tfidf_matrix[-1:], tfidf_matrix[:-1]).flatten()
                
                # Filtrar por threshold de similaridade
                similar_responses = []
                for i, similarity in enumerate(similarities):
                    if similarity >= similarity_threshold:
                        similar_emails[i]['similarity_score'] = float(similarity)
                        similar_responses.append(similar_emails[i])
                
                # Ordenar por similaridade
                similar_responses.sort(key=lambda x: x['similarity_score'], reverse=True)
                
                logger.info(f"Found {len(similar_responses)} similar responses")
                return similar_responses[:5]  # Top 5
                
            except Exception as e:
                logger.warning(f"TF-IDF similarity calculation failed: {e}")
                return similar_emails[:3]  # Fallback
            
        except Exception as e:
            logger.error(f"Error finding similar responses: {e}")
            return []
    
    def get_conversation_context(self, thread_id: str, account_name: str) -> Dict:
        """
        Analisa o contexto completo da conversa
        """
        try:
            conversation = self.gmail_service.get_conversation_thread(account_name, thread_id)
            
            if not conversation:
                return {}
            
            context = {
                'total_messages': len(conversation),
                'conversation_flow': [],
                'key_topics': [],
                'sentiment_progression': [],
                'last_response_style': None,
                'conversation_stage': self._determine_conversation_stage(conversation)
            }
            
            for msg in conversation:
                msg_analysis = {
                    'is_sent': msg.get('is_sent', False),
                    'timestamp': msg.get('received_at'),
                    'length': len(msg.get('body_text', '')),
                    'sentiment': self._analyze_sentiment(msg.get('body_text', '')),
                    'key_phrases': self._extract_key_phrases(msg.get('body_text', ''))
                }
                context['conversation_flow'].append(msg_analysis)
            
            # Analisar progressão do sentimento
            context['sentiment_progression'] = [
                msg['sentiment'] for msg in context['conversation_flow']
            ]
            
            # Identificar tópicos principais
            all_text = ' '.join([msg.get('body_text', '') for msg in conversation])
            context['key_topics'] = self._extract_keywords(all_text)
            
            # Analisar estilo da última resposta enviada
            last_sent = next((msg for msg in reversed(conversation) if msg.get('is_sent')), None)
            if last_sent:
                context['last_response_style'] = self._analyze_response_style(last_sent.get('body_text', ''))
            
            return context
            
        except Exception as e:
            logger.error(f"Error analyzing conversation context: {e}")
            return {}
    
    def generate_learning_insights(self, account_name: str) -> Dict:
        """
        Gera insights de aprendizado baseado no histórico completo
        """
        try:
            patterns = self.analyze_response_patterns(account_name)
            
            insights = {
                'response_effectiveness': self._analyze_response_effectiveness(account_name),
                'common_customer_questions': self._identify_common_questions(account_name),
                'optimal_response_times': self._analyze_response_timing(account_name),
                'successful_conversion_patterns': self._analyze_conversion_patterns(account_name),
                'improvement_suggestions': []
            }
            
            # Gerar sugestões de melhoria
            if patterns.get('response_length_stats', {}).get('avg_length', 0) > 500:
                insights['improvement_suggestions'].append(
                    "Considere respostas mais concisas - emails longos podem reduzir engajamento"
                )
            
            if len(patterns.get('greeting_patterns', [])) < 3:
                insights['improvement_suggestions'].append(
                    "Diversifique as saudações para tornar as respostas menos repetitivas"
                )
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating learning insights: {e}")
            return {}
    
    def _extract_response_templates(self, sent_emails: List[Dict]) -> List[Dict]:
        """Extrai templates de resposta comuns"""
        templates = []
        
        # Agrupar por estrutura similar
        structure_groups = defaultdict(list)
        
        for email in sent_emails:
            body = email.get('body_text', '')
            structure = self._get_email_structure(body)
            structure_groups[structure].append(email)
        
        # Criar templates para grupos com mais de 3 emails
        for structure, emails in structure_groups.items():
            if len(emails) >= 3:
                template = {
                    'structure': structure,
                    'usage_count': len(emails),
                    'example_subject': emails[0].get('subject', ''),
                    'common_phrases': self._extract_common_phrases(emails),
                    'avg_length': np.mean([len(e.get('body_text', '')) for e in emails])
                }
                templates.append(template)
        
        return sorted(templates, key=lambda x: x['usage_count'], reverse=True)
    
    def _extract_common_phrases(self, emails: List[Dict]) -> List[str]:
        """Extrai frases comuns dos emails"""
        all_text = ' '.join([email.get('body_text', '') for email in emails])
        
        # Extrair frases de 3-8 palavras
        phrases = re.findall(r'\b(?:\w+\s+){2,7}\w+\b', all_text.lower())
        
        # Contar frequência
        phrase_counts = Counter(phrases)
        
        # Filtrar frases muito comuns ou muito raras
        common_phrases = [
            phrase for phrase, count in phrase_counts.items()
            if count >= 2 and len(phrase.split()) >= 3
        ]
        
        return common_phrases[:20]  # Top 20
    
    def _extract_greeting_patterns(self, emails: List[Dict]) -> List[str]:
        """Extrai padrões de saudação"""
        greetings = []
        
        for email in emails:
            body = email.get('body_text', '')
            lines = body.split('\n')
            
            # Primeira linha não vazia
            for line in lines[:3]:
                line = line.strip()
                if line and len(line) < 100:
                    # Verificar se parece com saudação
                    if any(word in line.lower() for word in ['olá', 'oi', 'bom dia', 'boa tarde', 'prezado']):
                        greetings.append(line)
                        break
        
        return list(set(greetings))[:10]
    
    def _extract_closing_patterns(self, emails: List[Dict]) -> List[str]:
        """Extrai padrões de despedida"""
        closings = []
        
        for email in emails:
            body = email.get('body_text', '')
            lines = [line.strip() for line in body.split('\n') if line.strip()]
            
            # Últimas 3 linhas
            for line in lines[-3:]:
                if len(line) < 100:
                    # Verificar se parece com despedida
                    if any(word in line.lower() for word in ['atenciosamente', 'abraços', 'cordialmente', 'obrigado']):
                        closings.append(line)
                        break
        
        return list(set(closings))[:10]
    
    def _extract_subject_patterns(self, emails: List[Dict]) -> Dict:
        """Analisa padrões nos assuntos"""
        subjects = [email.get('subject', '') for email in emails if email.get('subject')]
        
        # Palavras mais comuns nos assuntos
        all_subjects = ' '.join(subjects).lower()
        words = re.findall(r'\b\w+\b', all_subjects)
        word_counts = Counter(words)
        
        return {
            'total_subjects': len(subjects),
            'common_words': dict(word_counts.most_common(10)),
            'avg_length': np.mean([len(s) for s in subjects]) if subjects else 0
        }
    
    def _analyze_tone_patterns(self, emails: List[Dict]) -> Dict:
        """Analisa padrões de tom nas respostas"""
        sentiments = []
        
        for email in emails:
            body = email.get('body_text', '')
            if body:
                blob = TextBlob(body)
                sentiments.append({
                    'polarity': blob.sentiment.polarity,
                    'subjectivity': blob.sentiment.subjectivity
                })
        
        if not sentiments:
            return {}
        
        return {
            'avg_polarity': np.mean([s['polarity'] for s in sentiments]),
            'avg_subjectivity': np.mean([s['subjectivity'] for s in sentiments]),
            'tone_consistency': np.std([s['polarity'] for s in sentiments])
        }
    
    def _analyze_response_lengths(self, emails: List[Dict]) -> Dict:
        """Analisa estatísticas de comprimento das respostas"""
        lengths = [len(email.get('body_text', '')) for email in emails]
        
        if not lengths:
            return {}
        
        return {
            'avg_length': np.mean(lengths),
            'median_length': np.median(lengths),
            'min_length': min(lengths),
            'max_length': max(lengths),
            'std_length': np.std(lengths)
        }
    
    def _extract_keyword_frequency(self, emails: List[Dict]) -> Dict:
        """Extrai frequência de palavras-chave importantes"""
        # Palavras-chave relacionadas ao negócio
        business_keywords = [
            'coaching', 'concurso', 'aprovação', 'estudo', 'metodologia',
            'sefaz', 'receita', 'fiscal', 'preparação', 'curso',
            'acelerador', 'mentoria', 'resultado', 'sucesso'
        ]
        
        all_text = ' '.join([email.get('body_text', '').lower() for email in emails])
        
        keyword_counts = {}
        for keyword in business_keywords:
            count = all_text.count(keyword)
            if count > 0:
                keyword_counts[keyword] = count
        
        return keyword_counts
    
    def _extract_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
        """Extrai palavras-chave principais do texto"""
        try:
            blob = TextBlob(text.lower())
            
            # Extrair substantivos e adjetivos
            keywords = []
            for word, pos in blob.tags:
                if pos in ['NN', 'NNS', 'JJ'] and len(word) > 3:
                    keywords.append(word)
            
            # Contar frequência
            keyword_counts = Counter(keywords)
            
            return [word for word, count in keyword_counts.most_common(max_keywords)]
            
        except Exception as e:
            logger.warning(f"Error extracting keywords: {e}")
            return []
    
    def _get_email_structure(self, body: str) -> str:
        """Identifica a estrutura básica do email"""
        lines = [line.strip() for line in body.split('\n') if line.strip()]
        
        if len(lines) <= 3:
            return "short"
        elif len(lines) <= 10:
            return "medium"
        else:
            return "long"
    
    def _analyze_sentiment(self, text: str) -> float:
        """Analisa sentimento do texto"""
        try:
            blob = TextBlob(text)
            return blob.sentiment.polarity
        except:
            return 0.0
    
    def _extract_key_phrases(self, text: str) -> List[str]:
        """Extrai frases-chave do texto"""
        try:
            # Extrair frases de 2-4 palavras
            phrases = re.findall(r'\b(?:\w+\s+){1,3}\w+\b', text.lower())
            
            # Filtrar frases relevantes
            relevant_phrases = [
                phrase for phrase in phrases
                if len(phrase.split()) >= 2 and len(phrase) > 5
            ]
            
            return list(set(relevant_phrases))[:10]
            
        except Exception as e:
            logger.warning(f"Error extracting key phrases: {e}")
            return []
    
    def _determine_conversation_stage(self, conversation: List[Dict]) -> str:
        """Determina o estágio da conversa"""
        if len(conversation) == 1:
            return "initial_contact"
        elif len(conversation) <= 3:
            return "early_engagement"
        elif len(conversation) <= 6:
            return "active_discussion"
        else:
            return "extended_conversation"
    
    def _analyze_response_style(self, text: str) -> Dict:
        """Analisa o estilo da resposta"""
        return {
            'length': len(text),
            'formality': self._assess_formality(text),
            'enthusiasm': self._assess_enthusiasm(text),
            'question_count': text.count('?'),
            'exclamation_count': text.count('!')
        }
    
    def _assess_formality(self, text: str) -> str:
        """Avalia o nível de formalidade"""
        formal_indicators = ['prezado', 'atenciosamente', 'cordialmente', 'senhor', 'senhora']
        informal_indicators = ['oi', 'olá', 'abraços', 'valeu', 'beleza']
        
        formal_count = sum(1 for indicator in formal_indicators if indicator in text.lower())
        informal_count = sum(1 for indicator in informal_indicators if indicator in text.lower())
        
        if formal_count > informal_count:
            return "formal"
        elif informal_count > formal_count:
            return "informal"
        else:
            return "neutral"
    
    def _assess_enthusiasm(self, text: str) -> str:
        """Avalia o nível de entusiasmo"""
        enthusiasm_indicators = ['excelente', 'ótimo', 'fantástico', 'incrível', 'perfeito']
        enthusiasm_count = sum(1 for indicator in enthusiasm_indicators if indicator in text.lower())
        exclamation_count = text.count('!')
        
        total_enthusiasm = enthusiasm_count + (exclamation_count * 0.5)
        
        if total_enthusiasm >= 3:
            return "high"
        elif total_enthusiasm >= 1:
            return "medium"
        else:
            return "low"
    
    def _analyze_response_effectiveness(self, account_name: str) -> Dict:
        """Analisa efetividade das respostas (placeholder)"""
        # Esta funcionalidade requereria métricas de engajamento
        return {"status": "requires_engagement_metrics"}
    
    def _identify_common_questions(self, account_name: str) -> List[str]:
        """Identifica perguntas comuns (placeholder)"""
        # Analisaria emails recebidos para identificar padrões de perguntas
        return ["requires_received_emails_analysis"]
    
    def _analyze_response_timing(self, account_name: str) -> Dict:
        """Analisa timing de respostas (placeholder)"""
        return {"status": "requires_conversation_threading"}
    
    def _analyze_conversion_patterns(self, account_name: str) -> Dict:
        """Analisa padrões de conversão (placeholder)"""
        return {"status": "requires_conversion_tracking"}
