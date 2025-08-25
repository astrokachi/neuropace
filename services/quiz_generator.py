import random
import re
from typing import List, Dict, Any, Optional
from config import settings

class QuizGenerator:
    """Service for generating quizzes from text content"""
    
    @staticmethod
    def generate_quiz_from_text(
        text: str, 
        num_questions: int = None,
        difficulty_level: float = 0.5,
        content_section: str = None
    ) -> Dict[str, Any]:
        """
        Generate a quiz from text content
        
        Args:
            text: Text content to generate quiz from
            num_questions: Number of questions to generate
            difficulty_level: Difficulty level (0.0 to 1.0)
            content_section: Section identifier for the content
            
        Returns:
            Dictionary containing quiz data
        """
        if num_questions is None:
            num_questions = settings.QUIZ_QUESTIONS_PER_SECTION
        
        try:
            # Extract potential quiz content
            sentences = QuizGenerator._extract_sentences(text)
            facts = QuizGenerator._extract_facts(text)
            definitions = QuizGenerator._extract_definitions(text)
            
            if not sentences and not facts:
                return {
                    'success': False,
                    'error': 'Insufficient content for quiz generation',
                    'questions': []
                }
            
            questions = []
            
            # Generate different types of questions
            question_types = [
                ('multiple_choice', 0.6),
                ('true_false', 0.3),
                ('fill_blank', 0.1)
            ]
            
            # Adjust question types based on difficulty
            if difficulty_level < 0.3:
                # Easier questions - more true/false
                question_types = [('true_false', 0.5), ('multiple_choice', 0.5)]
            elif difficulty_level > 0.7:
                # Harder questions - more fill in the blank and complex multiple choice
                question_types = [('multiple_choice', 0.5), ('fill_blank', 0.3), ('true_false', 0.2)]
            
            # Generate questions
            for i in range(min(num_questions, len(sentences))):
                question_type = QuizGenerator._select_question_type(question_types)
                
                if question_type == 'multiple_choice':
                    question = QuizGenerator._generate_multiple_choice(sentences, facts, i)
                elif question_type == 'true_false':
                    question = QuizGenerator._generate_true_false(sentences, i)
                elif question_type == 'fill_blank':
                    question = QuizGenerator._generate_fill_blank(sentences, i)
                else:
                    question = QuizGenerator._generate_multiple_choice(sentences, facts, i)
                
                if question:
                    questions.append(question)
            
            return {
                'success': True,
                'questions': questions,
                'total_questions': len(questions),
                'difficulty_level': difficulty_level,
                'content_section': content_section
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Quiz generation failed: {str(e)}',
                'questions': []
            }
    
    @staticmethod
    def _extract_sentences(text: str) -> List[str]:
        """Extract meaningful sentences from text"""
        # Split by sentence-ending punctuation
        sentences = re.split(r'[.!?]+', text)
        
        # Filter and clean sentences
        meaningful_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            # Keep sentences that are not too short or too long
            if 10 <= len(sentence.split()) <= 50:
                meaningful_sentences.append(sentence)
        
        return meaningful_sentences
    
    @staticmethod
    def _extract_facts(text: str) -> List[str]:
        """Extract factual statements from text"""
        facts = []
        sentences = QuizGenerator._extract_sentences(text)
        
        # Look for sentences that contain factual patterns
        fact_patterns = [
            r'\b\d+\b',  # Contains numbers
            r'\b(is|are|was|were|has|have|had)\b',  # Contains state verbs
            r'\b(according to|research shows|studies indicate)\b',  # Research references
            r'\b(defined as|refers to|means)\b'  # Definitions
        ]
        
        for sentence in sentences:
            for pattern in fact_patterns:
                if re.search(pattern, sentence, re.IGNORECASE):
                    facts.append(sentence)
                    break
        
        return facts
    
    @staticmethod
    def _extract_definitions(text: str) -> List[Dict[str, str]]:
        """Extract term definitions from text"""
        definitions = []
        
        # Look for definition patterns
        definition_patterns = [
            r'(\b[A-Z][a-z]+\b)\s+(?:is|are|refers to|means|defined as)\s+([^.!?]+)',
            r'(\b[A-Z][a-z]+\b):\s*([^.!?]+)',
        ]
        
        for pattern in definition_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                term = match.group(1)
                definition = match.group(2).strip()
                if len(definition.split()) >= 3:  # Ensure definition is meaningful
                    definitions.append({'term': term, 'definition': definition})
        
        return definitions
    
    @staticmethod
    def _select_question_type(question_types: List[tuple]) -> str:
        """Select question type based on weights"""
        total_weight = sum(weight for _, weight in question_types)
        r = random.random() * total_weight
        
        cumulative_weight = 0
        for q_type, weight in question_types:
            cumulative_weight += weight
            if r <= cumulative_weight:
                return q_type
        
        return question_types[0][0]  # Fallback
    
    @staticmethod
    def _generate_multiple_choice(sentences: List[str], facts: List[str], index: int) -> Optional[Dict[str, Any]]:
        """Generate a multiple choice question"""
        try:
            if index >= len(sentences):
                return None
            
            base_sentence = sentences[index]
            
            # Extract key information from sentence
            words = base_sentence.split()
            if len(words) < 5:
                return None
            
            # Find a good word to ask about (noun or important term)
            important_words = [word for word in words if len(word) > 4 and word.isalpha()]
            if not important_words:
                return None
            
            target_word = random.choice(important_words)
            
            # Create question by replacing the target word
            question_text = base_sentence.replace(target_word, "______")
            
            # Generate answer options
            options = [target_word]  # Correct answer
            
            # Generate distractors
            all_words = []
            for sentence in sentences[:20]:  # Use first 20 sentences for distractors
                all_words.extend([word for word in sentence.split() if len(word) > 4 and word.isalpha()])
            
            distractors = list(set(all_words) - {target_word})
            random.shuffle(distractors)
            
            # Add 3 distractors
            options.extend(distractors[:3])
            
            # Shuffle options
            correct_index = 0
            random.shuffle(options)
            correct_index = options.index(target_word)
            
            return {
                'type': 'multiple_choice',
                'question': f'Fill in the blank: {question_text}',
                'options': options,
                'correct_answer': correct_index,
                'explanation': f'The correct answer is "{target_word}" based on the context provided.'
            }
            
        except Exception as e:
            print(f"Error generating multiple choice question: {e}")
            return None
    
    @staticmethod
    def _generate_true_false(sentences: List[str], index: int) -> Optional[Dict[str, Any]]:
        """Generate a true/false question"""
        try:
            if index >= len(sentences):
                return None
            
            base_sentence = sentences[index]
            
            # Randomly decide if this should be true or false
            is_true = random.choice([True, False])
            
            if is_true:
                # Use the sentence as-is
                question_text = base_sentence
                correct_answer = 0  # True
                explanation = "This statement is true based on the provided content."
            else:
                # Modify the sentence to make it false
                words = base_sentence.split()
                if len(words) < 5:
                    return None
                
                # Simple modifications to make false
                modifications = [
                    lambda s: s.replace(' is ', ' is not '),
                    lambda s: s.replace(' are ', ' are not '),
                    lambda s: s.replace(' can ', ' cannot '),
                    lambda s: s.replace(' will ', ' will not ')
                ]
                
                modification = random.choice(modifications)
                question_text = modification(base_sentence)
                
                # If no modification was made, try word replacement
                if question_text == base_sentence and len(words) > 3:
                    # Replace a key word with an antonym or different word
                    replacements = {
                        'increase': 'decrease',
                        'large': 'small',
                        'high': 'low',
                        'important': 'unimportant',
                        'effective': 'ineffective',
                        'positive': 'negative',
                        'good': 'bad',
                        'always': 'never',
                        'all': 'none'
                    }
                    
                    for word in words:
                        if word.lower() in replacements:
                            question_text = base_sentence.replace(word, replacements[word.lower()])
                            break
                
                correct_answer = 1  # False
                explanation = "This statement is false. The original content states something different."
            
            return {
                'type': 'true_false',
                'question': question_text,
                'options': ['True', 'False'],
                'correct_answer': correct_answer,
                'explanation': explanation
            }
            
        except Exception as e:
            print(f"Error generating true/false question: {e}")
            return None
    
    @staticmethod
    def _generate_fill_blank(sentences: List[str], index: int) -> Optional[Dict[str, Any]]:
        """Generate a fill-in-the-blank question"""
        try:
            if index >= len(sentences):
                return None
            
            base_sentence = sentences[index]
            words = base_sentence.split()
            
            if len(words) < 6:
                return None
            
            # Find important words to blank out
            important_words = []
            for i, word in enumerate(words):
                if (len(word) > 4 and 
                    word.isalpha() and 
                    word.lower() not in ['the', 'and', 'or', 'but', 'with', 'from', 'they', 'this', 'that']):
                    important_words.append((i, word))
            
            if not important_words:
                return None
            
            # Select word to blank out
            word_index, target_word = random.choice(important_words)
            
            # Create question with blank
            question_words = words.copy()
            question_words[word_index] = "______"
            question_text = " ".join(question_words)
            
            return {
                'type': 'fill_blank',
                'question': f'Fill in the blank: {question_text}',
                'options': [target_word],  # For fill-in-blank, we store the answer in options[0]
                'correct_answer': 0,
                'explanation': f'The correct answer is "{target_word}".'
            }
            
        except Exception as e:
            print(f"Error generating fill blank question: {e}")
            return None
    
    @staticmethod
    def validate_quiz_answers(quiz_questions: List[Dict[str, Any]], user_answers: List[Any]) -> Dict[str, Any]:
        """
        Validate user answers against quiz questions
        
        Args:
            quiz_questions: List of quiz question dictionaries
            user_answers: List of user answers (indices or strings)
            
        Returns:
            Dictionary with validation results
        """
        if len(quiz_questions) != len(user_answers):
            return {
                'success': False,
                'error': 'Mismatch between questions and answers count'
            }
        
        correct_count = 0
        total_questions = len(quiz_questions)
        detailed_results = []
        
        for i, (question, user_answer) in enumerate(zip(quiz_questions, user_answers)):
            correct_answer = question.get('correct_answer', 0)
            is_correct = False
            
            # Handle different answer formats
            if question.get('type') == 'fill_blank':
                # For fill-in-the-blank, check if answer matches (case-insensitive)
                expected = question['options'][0].lower().strip()
                given = str(user_answer).lower().strip()
                is_correct = expected == given
            else:
                # For multiple choice and true/false, check index
                try:
                    is_correct = int(user_answer) == correct_answer
                except (ValueError, TypeError):
                    is_correct = False
            
            if is_correct:
                correct_count += 1
            
            detailed_results.append({
                'question_index': i,
                'user_answer': user_answer,
                'correct_answer': correct_answer,
                'is_correct': is_correct,
                'explanation': question.get('explanation', '')
            })
        
        score = correct_count / total_questions if total_questions > 0 else 0
        
        return {
            'success': True,
            'score': score,
            'correct_count': correct_count,
            'total_questions': total_questions,
            'detailed_results': detailed_results
        }
