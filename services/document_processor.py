"""
Enhanced Document Processor with ML-driven content analysis
Implements advanced document processing pipeline from system architecture
"""

import pypdf as PyPDF2
import os
import re
import math
from typing import Dict, Any, Optional, List
from io import BytesIO
import numpy as np
from collections import Counter
from sqlalchemy.orm import Session

class DocumentProcessor:
    """
    Enhanced document processing service with ML-driven content analysis
    Supports multiple document types with advanced text analytics
    """
    
    def __init__(self):
        # Initialize TF-IDF and other NLP components
        self.stop_words = set([
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
            'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during',
            'before', 'after', 'above', 'below', 'is', 'are', 'was', 'were', 'be',
            'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
            'would', 'could', 'should', 'this', 'that', 'these', 'those'
        ])
    
    def process_document(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """
        Complete document processing pipeline with ML analysis
        
        Args:
            file_content: Raw file content as bytes
            filename: Name of the uploaded file
            
        Returns:
            Comprehensive document analysis results
        """
        try:
            # Step 1: Text Extraction
            extraction_result = self._extract_text_content(file_content, filename)
            if not extraction_result['success']:
                return extraction_result
            
            # Step 2: Content Structure Analysis
            structure_analysis = self.analyze_content_structure(extraction_result['full_text'])
            
            # Step 3: Readability and Difficulty Analysis
            readability_analysis = self._advanced_readability_analysis(extraction_result['full_text'])
            
            # Step 4: Keyword and Topic Extraction
            keyword_analysis = self._extract_keywords_and_topics(extraction_result['full_text'])
            
            # Step 5: Learning Objective Identification
            learning_objectives = self._identify_learning_objectives(extraction_result['full_text'])
            
            # Step 6: Content Segmentation for Optimal Learning
            content_segments = self._intelligent_content_segmentation(
                extraction_result['full_text'],
                readability_analysis['difficulty_score']
            )
            
            return {
                'success': True,
                'full_text': extraction_result['full_text'],
                'metadata': extraction_result['metadata'],
                'structure_analysis': structure_analysis,
                'readability_analysis': readability_analysis,
                'keyword_analysis': keyword_analysis,
                'learning_objectives': learning_objectives,
                'content_segments': content_segments,
                'processing_metadata': {
                    'processed_at': extraction_result['metadata'].get('processed_at'),
                    'processor_version': '2.0',
                    'analysis_methods': ['flesch_reading_ease', 'tf_idf', 'semantic_segmentation']
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Document processing failed: {str(e)}',
                'stage': 'document_processing'
            }
    
    def analyze_content_structure(self, text: str) -> Dict[str, Any]:
        """
        Advanced content structure analysis
        
        Args:
            text: Full text content
            
        Returns:
            Detailed structure analysis
        """
        try:
            # Basic text statistics
            words = text.split()
            sentences = re.split(r'[.!?]+', text)
            sentences = [s.strip() for s in sentences if s.strip()]
            paragraphs = text.split('\n\n')
            paragraphs = [p.strip() for p in paragraphs if p.strip()]
            
            # Advanced metrics
            avg_sentence_length = len(words) / len(sentences) if sentences else 0
            avg_paragraph_length = len(sentences) / len(paragraphs) if paragraphs else 0
            
            # Complexity indicators
            complex_words = [w for w in words if len(w) > 6 and not w.lower() in self.stop_words]
            technical_terms = self._identify_technical_terms(words)
            
            # Estimated difficulty
            difficulty_score = self._calculate_advanced_difficulty(text, words, sentences)
            
            # Reading time estimation with user adaptation
            base_reading_speed = 200  # words per minute
            adjusted_speed = base_reading_speed * (1 - (difficulty_score * 0.3))  # Slower for difficult text
            estimated_reading_time = len(words) / adjusted_speed
            
            return {
                'word_count': len(words),
                'sentence_count': len(sentences),
                'paragraph_count': len(paragraphs),
                'character_count': len(text),
                'avg_sentence_length': round(avg_sentence_length, 2),
                'avg_paragraph_length': round(avg_paragraph_length, 2),
                'complex_word_ratio': len(complex_words) / len(words) if words else 0,
                'technical_term_count': len(technical_terms),
                'technical_terms': technical_terms[:10],  # Top 10 technical terms
                'estimated_difficulty': difficulty_score,
                'estimated_reading_time': round(estimated_reading_time, 2),
                'content_density': self._calculate_content_density(text),
                'structural_complexity': self._analyze_structural_complexity(paragraphs)
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'word_count': 0,
                'estimated_difficulty': 0.5,
                'estimated_reading_time': 0
            }
    
    def optimize_content_selection(
        self,
        material_id: int,
        available_time: int,
        user_reading_speed: float,
        difficulty_preference: float
    ) -> Dict[str, Any]:
        """
        Optimize content selection for study sessions
        
        Args:
            material_id: ID of the material
            available_time: Available study time in minutes
            user_reading_speed: User's reading speed (words per minute)
            difficulty_preference: User's difficulty tolerance (0.0-1.0)
            
        Returns:
            Optimized content selection
        """
        try:
            # This would typically retrieve material from database
            # For now, we'll simulate the optimization logic
            
            # Calculate optimal word count for session
            max_words = int(available_time * user_reading_speed)
            
            # Adjust for difficulty preference
            difficulty_adjustment = 1.0 - (difficulty_preference * 0.3)
            adjusted_word_count = int(max_words * difficulty_adjustment)
            
            # Create recommended sections (simulated)
            recommended_sections = [
                {
                    'section_id': f'section_{i+1}',
                    'title': f'Section {i+1}',
                    'word_count': min(500, adjusted_word_count // 3),
                    'estimated_time': min(15, available_time // 3),
                    'difficulty_score': min(difficulty_preference + 0.1, 1.0),
                    'content_type': 'reading',
                    'learning_objectives': [f'Objective {i+1}.1', f'Objective {i+1}.2']
                }
                for i in range(min(3, available_time // 15))  # Max 3 sections, 15 min minimum each
            ]
            
            return {
                'success': True,
                'recommended_sections': recommended_sections,
                'optimization_factors': {
                    'available_time': available_time,
                    'user_reading_speed': user_reading_speed,
                    'difficulty_preference': difficulty_preference,
                    'total_estimated_time': sum(s['estimated_time'] for s in recommended_sections)
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'recommended_sections': []
            }
    
    def _extract_text_content(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """Enhanced text extraction with multiple format support"""
        file_extension = os.path.splitext(filename)[1].lower()
        
        if file_extension == '.pdf':
            return self._extract_pdf_content(file_content, filename)
        elif file_extension in ['.txt', '.md']:
            return self._extract_text_content_simple(file_content, filename)
        else:
            return {
                'success': False,
                'error': f'Unsupported file format: {file_extension}',
                'supported_formats': ['.pdf', '.txt', '.md']
            }
    
    def _extract_pdf_content(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """Extract content from PDF with enhanced metadata"""
        try:
            pdf_reader = PyPDF2.PdfReader(BytesIO(file_content))
            
            # Enhanced metadata extraction
            metadata = {
                'filename': filename,
                'total_pages': len(pdf_reader.pages),
                'title': '',
                'author': '',
                'subject': '',
                'creator': '',
                'producer': '',
                'creation_date': None,
                'modification_date': None
            }
            
            # Extract PDF metadata if available
            if pdf_reader.metadata:
                metadata.update({
                    'title': pdf_reader.metadata.get('/Title', ''),
                    'author': pdf_reader.metadata.get('/Author', ''),
                    'subject': pdf_reader.metadata.get('/Subject', ''),
                    'creator': pdf_reader.metadata.get('/Creator', ''),
                    'producer': pdf_reader.metadata.get('/Producer', ''),
                    'creation_date': pdf_reader.metadata.get('/CreationDate'),
                    'modification_date': pdf_reader.metadata.get('/ModDate')
                })
            
            # Extract text with page-level analysis
            full_text = ""
            page_analyses = []
            
            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    page_text = page.extract_text()
                    page_word_count = len(page_text.split()) if page_text else 0
                    
                    page_analyses.append({
                        'page_number': page_num + 1,
                        'text': page_text,
                        'word_count': page_word_count,
                        'character_count': len(page_text) if page_text else 0,
                        'estimated_reading_time': self._estimate_reading_time(page_word_count)
                    })
                    
                    full_text += page_text + "\n"
                    
                except Exception as e:
                    page_analyses.append({
                        'page_number': page_num + 1,
                        'text': '',
                        'word_count': 0,
                        'character_count': 0,
                        'error': str(e)
                    })
            
            return {
                'success': True,
                'full_text': full_text,
                'metadata': metadata,
                'page_analyses': page_analyses,
                'extraction_method': 'pypdf'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'full_text': '',
                'metadata': {'filename': filename}
            }
    
    def _extract_text_content_simple(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """Extract content from text files"""
        try:
            text = file_content.decode('utf-8')
            word_count = len(text.split())
            
            return {
                'success': True,
                'full_text': text,
                'metadata': {
                    'filename': filename,
                    'word_count': word_count,
                    'character_count': len(text),
                    'estimated_reading_time': self._estimate_reading_time(word_count)
                },
                'extraction_method': 'text_decode'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'full_text': '',
                'metadata': {'filename': filename}
            }
    
    def _advanced_readability_analysis(self, text: str) -> Dict[str, Any]:
        """Advanced readability analysis using multiple metrics"""
        if not text or not text.strip():
            return {'difficulty_score': 0.5, 'readability_metrics': {}}
        
        words = text.split()
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not words or not sentences:
            return {'difficulty_score': 0.5, 'readability_metrics': {}}
        
        # Basic metrics
        avg_sentence_length = len(words) / len(sentences)
        avg_word_length = sum(len(word) for word in words) / len(words)
        
        # Syllable counting for more accurate analysis
        total_syllables = sum(self._count_syllables(word) for word in words)
        avg_syllables_per_word = total_syllables / len(words)
        
        # Flesch Reading Ease Score
        flesch_score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
        
        # Flesch-Kincaid Grade Level
        fk_grade = (0.39 * avg_sentence_length) + (11.8 * avg_syllables_per_word) - 15.59
        
        # Gunning Fog Index
        complex_words = [w for w in words if self._count_syllables(w) >= 3]
        complex_word_ratio = len(complex_words) / len(words)
        gunning_fog = 0.4 * (avg_sentence_length + (100 * complex_word_ratio))
        
        # SMOG Index (simplified)
        smog_index = 1.043 * math.sqrt(complex_word_ratio * 30) + 3.1291
        
        # Convert to normalized difficulty score (0.0 = easy, 1.0 = very difficult)
        difficulty_indicators = [
            max(0, min(1, (100 - flesch_score) / 100)),  # Flesch (inverted)
            max(0, min(1, fk_grade / 20)),  # FK Grade normalized
            max(0, min(1, gunning_fog / 20)),  # Gunning Fog normalized
            max(0, min(1, smog_index / 20)),  # SMOG normalized
            complex_word_ratio  # Complex word ratio
        ]
        
        # Weighted average of difficulty indicators
        difficulty_score = sum(difficulty_indicators) / len(difficulty_indicators)
        
        return {
            'difficulty_score': round(difficulty_score, 3),
            'readability_metrics': {
                'flesch_reading_ease': round(flesch_score, 2),
                'flesch_kincaid_grade': round(fk_grade, 2),
                'gunning_fog_index': round(gunning_fog, 2),
                'smog_index': round(smog_index, 2),
                'average_sentence_length': round(avg_sentence_length, 2),
                'average_word_length': round(avg_word_length, 2),
                'average_syllables_per_word': round(avg_syllables_per_word, 2),
                'complex_word_percentage': round(complex_word_ratio * 100, 2)
            },
            'readability_level': self._get_readability_level(difficulty_score)
        }
    
    def _extract_keywords_and_topics(self, text: str) -> Dict[str, Any]:
        """Extract keywords and topics using TF-IDF analysis"""
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        words = [w for w in words if w not in self.stop_words]
        
        if not words:
            return {'keywords': [], 'topics': [], 'word_frequency': {}}
        
        # Word frequency analysis
        word_freq = Counter(words)
        total_words = len(words)
        
        # Calculate TF-IDF scores (simplified)
        tf_scores = {word: freq / total_words for word, freq in word_freq.items()}
        
        # Identify keywords (high frequency, non-common words)
        keywords = sorted(tf_scores.items(), key=lambda x: x[1], reverse=True)[:20]
        
        # Topic identification (simplified clustering of related terms)
        topics = self._identify_topics(keywords)
        
        return {
            'keywords': [{'word': word, 'score': round(score, 4)} for word, score in keywords],
            'topics': topics,
            'word_frequency': dict(word_freq.most_common(50)),
            'vocabulary_diversity': len(set(words)) / len(words),
            'total_unique_words': len(set(words))
        }
    
    def _identify_learning_objectives(self, text: str) -> List[Dict[str, Any]]:
        """Identify potential learning objectives from content"""
        # Simplified pattern matching for learning objectives
        objective_patterns = [
            r'understand\s+([^.]+)',
            r'learn\s+about\s+([^.]+)',
            r'explain\s+([^.]+)',
            r'describe\s+([^.]+)',
            r'analyze\s+([^.]+)',
            r'identify\s+([^.]+)',
            r'define\s+([^.]+)'
        ]
        
        objectives = []
        for pattern in objective_patterns:
            matches = re.finditer(pattern, text.lower())
            for match in matches:
                objective_text = match.group(1).strip()
                if len(objective_text) > 5 and len(objective_text) < 100:
                    objectives.append({
                        'objective': objective_text.capitalize(),
                        'type': pattern.split('\\s+')[0],
                        'confidence': 0.7  # Simple confidence score
                    })
        
        # Remove duplicates and limit to top objectives
        unique_objectives = []
        seen = set()
        for obj in objectives:
            if obj['objective'] not in seen:
                unique_objectives.append(obj)
                seen.add(obj['objective'])
                if len(unique_objectives) >= 10:
                    break
        
        return unique_objectives
    
    def _intelligent_content_segmentation(self, text: str, difficulty_score: float) -> List[Dict[str, Any]]:
        """Intelligent content segmentation for optimal learning"""
        paragraphs = text.split('\n\n')
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        
        # Adaptive section size based on difficulty
        base_words_per_section = 400
        difficulty_adjustment = 1.0 - (difficulty_score * 0.4)  # Smaller sections for difficult content
        target_words_per_section = int(base_words_per_section * difficulty_adjustment)
        
        segments = []
        current_segment = ""
        current_word_count = 0
        segment_number = 1
        
        for para in paragraphs:
            para_words = len(para.split())
            
            if current_word_count + para_words > target_words_per_section and current_segment:
                # Create segment
                segment_analysis = self._analyze_segment(current_segment)
                segments.append({
                    'segment_number': segment_number,
                    'content': current_segment.strip(),
                    'word_count': current_word_count,
                    'estimated_reading_time': self._estimate_reading_time(current_word_count),
                    'difficulty_score': segment_analysis['difficulty'],
                    'key_concepts': segment_analysis['key_concepts'],
                    'cognitive_load': self._estimate_cognitive_load(current_segment, difficulty_score)
                })
                
                current_segment = para
                current_word_count = para_words
                segment_number += 1
            else:
                current_segment += "\n\n" + para if current_segment else para
                current_word_count += para_words
        
        # Add final segment
        if current_segment.strip():
            segment_analysis = self._analyze_segment(current_segment)
            segments.append({
                'segment_number': segment_number,
                'content': current_segment.strip(),
                'word_count': current_word_count,
                'estimated_reading_time': self._estimate_reading_time(current_word_count),
                'difficulty_score': segment_analysis['difficulty'],
                'key_concepts': segment_analysis['key_concepts'],
                'cognitive_load': self._estimate_cognitive_load(current_segment, difficulty_score)
            })
        
        return segments
    
    def _analyze_segment(self, segment_text: str) -> Dict[str, Any]:
        """Analyze individual content segment"""
        words = segment_text.split()
        
        # Extract key concepts (simplified)
        important_words = [w for w in words if len(w) > 5 and w.lower() not in self.stop_words]
        word_freq = Counter(important_words)
        key_concepts = [word for word, freq in word_freq.most_common(5)]
        
        # Calculate segment difficulty
        difficulty = self._calculate_segment_difficulty(segment_text)
        
        return {
            'key_concepts': key_concepts,
            'difficulty': difficulty
        }
    
    def _calculate_advanced_difficulty(self, text: str, words: List[str], sentences: List[str]) -> float:
        """Calculate advanced difficulty score"""
        if not words or not sentences:
            return 0.5
        
        # Multiple difficulty factors
        factors = []
        
        # 1. Average sentence length
        avg_sentence_length = len(words) / len(sentences)
        factors.append(min(1.0, avg_sentence_length / 25.0))  # Normalize to 25 words max
        
        # 2. Average word length
        avg_word_length = sum(len(word) for word in words) / len(words)
        factors.append(min(1.0, (avg_word_length - 3) / 5.0))  # Normalize to 3-8 chars
        
        # 3. Complex word ratio
        complex_words = [w for w in words if len(w) > 6]
        factors.append(len(complex_words) / len(words))
        
        # 4. Technical term density
        technical_terms = self._identify_technical_terms(words)
        factors.append(min(1.0, len(technical_terms) / (len(words) / 100)))  # Per 100 words
        
        # 5. Syllable complexity
        total_syllables = sum(self._count_syllables(word) for word in words)
        avg_syllables = total_syllables / len(words)
        factors.append(min(1.0, (avg_syllables - 1) / 2.0))  # Normalize to 1-3 syllables
        
        # Weighted average
        weights = [0.2, 0.15, 0.25, 0.2, 0.2]
        difficulty = sum(f * w for f, w in zip(factors, weights))
        
        return min(1.0, max(0.0, difficulty))
    
    def _identify_technical_terms(self, words: List[str]) -> List[str]:
        """Identify technical terms in the text"""
        # Simple heuristics for technical terms
        technical_terms = []
        
        for word in words:
            word_lower = word.lower()
            # Skip if it's a common word
            if word_lower in self.stop_words:
                continue
            
            # Heuristics for technical terms
            if (len(word) > 8 or  # Long words
                word.isupper() or  # Acronyms
                '_' in word or  # Underscore terms
                any(char.isdigit() for char in word) or  # Contains numbers
                word.endswith(('tion', 'sion', 'ment', 'ness', 'ity', 'ism'))):  # Technical suffixes
                technical_terms.append(word)
        
        return list(set(technical_terms))  # Remove duplicates
    
    def _calculate_content_density(self, text: str) -> float:
        """Calculate information density of content"""
        words = text.split()
        if not words:
            return 0.0
        
        # Information markers
        info_words = ['however', 'therefore', 'because', 'although', 'moreover', 'furthermore']
        info_count = sum(1 for word in words if word.lower() in info_words)
        
        # Question marks (indicate complexity)
        question_count = text.count('?')
        
        # Numbers and data points
        number_count = sum(1 for word in words if any(char.isdigit() for char in word))
        
        # Calculate density score
        density = (info_count + question_count + number_count) / len(words)
        return min(1.0, density * 10)  # Scale to 0-1 range
    
    def _analyze_structural_complexity(self, paragraphs: List[str]) -> float:
        """Analyze structural complexity of the document"""
        if not paragraphs:
            return 0.0
        
        # Variation in paragraph lengths
        para_lengths = [len(p.split()) for p in paragraphs]
        if not para_lengths:
            return 0.0
        
        avg_length = sum(para_lengths) / len(para_lengths)
        variance = sum((l - avg_length) ** 2 for l in para_lengths) / len(para_lengths)
        
        # Normalize structural complexity
        complexity = min(1.0, variance / (avg_length ** 2) if avg_length > 0 else 0)
        return complexity
    
    def _identify_topics(self, keywords: List[tuple]) -> List[Dict[str, Any]]:
        """Identify topics from keywords (simplified clustering)"""
        if not keywords:
            return []
        
        # Simple topic identification based on keyword co-occurrence
        # In a real implementation, this would use more sophisticated NLP
        topics = []
        used_words = set()
        
        for word, score in keywords[:10]:  # Top 10 keywords
            if word not in used_words:
                # Create a topic centered around this keyword
                topic_words = [word]
                used_words.add(word)
                
                # Find related words (simple similarity based on shared characters)
                for other_word, other_score in keywords:
                    if other_word not in used_words and len(set(word) & set(other_word)) >= 3:
                        topic_words.append(other_word)
                        used_words.add(other_word)
                        if len(topic_words) >= 3:
                            break
                
                topics.append({
                    'topic_name': word.capitalize(),
                    'keywords': topic_words,
                    'relevance_score': round(score, 3)
                })
                
                if len(topics) >= 5:  # Limit to 5 topics
                    break
        
        return topics
    
    def _calculate_segment_difficulty(self, segment: str) -> float:
        """Calculate difficulty for a text segment"""
        words = segment.split()
        if not words:
            return 0.5
        
        # Simple difficulty calculation for segments
        complex_words = [w for w in words if len(w) > 6]
        complexity_ratio = len(complex_words) / len(words)
        
        sentences = re.split(r'[.!?]+', segment)
        sentences = [s.strip() for s in sentences if s.strip()]
        avg_sentence_length = len(words) / len(sentences) if sentences else 0
        
        # Combine factors
        difficulty = (complexity_ratio * 0.6) + min(1.0, avg_sentence_length / 20.0) * 0.4
        return min(1.0, max(0.0, difficulty))
    
    def _estimate_cognitive_load(self, text: str, base_difficulty: float) -> float:
        """Estimate cognitive load for a text segment"""
        words = text.split()
        
        # Factors affecting cognitive load
        word_count_factor = min(1.0, len(words) / 500.0)  # More words = higher load
        difficulty_factor = base_difficulty
        
        # Information density factor
        info_density = self._calculate_content_density(text)
        
        # Combine factors
        cognitive_load = (word_count_factor * 0.3) + (difficulty_factor * 0.5) + (info_density * 0.2)
        return min(1.0, cognitive_load)
    
    def _count_syllables(self, word: str) -> int:
        """Count syllables in a word (improved algorithm)"""
        word = word.lower().strip('.,!?;:"')
        if not word:
            return 0
        
        vowels = 'aeiouy'
        syllable_count = 0
        previous_was_vowel = False
        
        for i, char in enumerate(word):
            is_vowel = char in vowels
            if is_vowel and not previous_was_vowel:
                syllable_count += 1
            previous_was_vowel = is_vowel
        
        # Handle silent 'e'
        if word.endswith('e') and syllable_count > 1:
            syllable_count -= 1
        
        # Handle 'le' endings
        if word.endswith('le') and len(word) > 2 and word[-3] not in vowels:
            syllable_count += 1
        
        return max(1, syllable_count)
    
    def _estimate_reading_time(self, word_count: int, reading_speed: float = 200.0) -> float:
        """Estimate reading time with improved accuracy"""
        if word_count <= 0:
            return 0.0
        return round(word_count / reading_speed, 2)
    
    def _get_readability_level(self, difficulty_score: float) -> str:
        """Convert difficulty score to readability level"""
        if difficulty_score <= 0.2:
            return "Very Easy"
        elif difficulty_score <= 0.4:
            return "Easy"
        elif difficulty_score <= 0.6:
            return "Moderate"
        elif difficulty_score <= 0.8:
            return "Difficult"
        else:
            return "Very Difficult"