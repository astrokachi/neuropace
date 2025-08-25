import pypdf as PyPDF2
import os
import re
from typing import Dict, Any, Optional, List
from io import BytesIO

class PDFProcessor:
    """Service for processing PDF files and extracting text content"""
    
    @staticmethod
    def extract_text_from_pdf(file_path: str) -> Dict[str, Any]:
        """
        Extract text content from PDF file
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Dictionary containing extracted text and metadata
        """
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Extract metadata
                metadata = {
                    'total_pages': len(pdf_reader.pages),
                    'title': '',
                    'author': '',
                    'subject': ''
                }
                
                # Get document info if available
                if pdf_reader.metadata:
                    metadata.update({
                        'title': pdf_reader.metadata.get('/Title', ''),
                        'author': pdf_reader.metadata.get('/Author', ''),
                        'subject': pdf_reader.metadata.get('/Subject', '')
                    })
                
                # Extract text from all pages
                full_text = ""
                page_texts = []
                
                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        page_text = page.extract_text()
                        page_texts.append({
                            'page_number': page_num + 1,
                            'text': page_text,
                            'word_count': len(page_text.split()) if page_text else 0
                        })
                        full_text += page_text + "\n"
                    except Exception as e:
                        print(f"Error extracting text from page {page_num + 1}: {e}")
                        page_texts.append({
                            'page_number': page_num + 1,
                            'text': '',
                            'word_count': 0,
                            'error': str(e)
                        })
                
                # Calculate statistics
                word_count = len(full_text.split()) if full_text else 0
                char_count = len(full_text)
                
                return {
                    'success': True,
                    'full_text': full_text,
                    'page_texts': page_texts,
                    'metadata': metadata,
                    'statistics': {
                        'word_count': word_count,
                        'char_count': char_count,
                        'estimated_reading_time': PDFProcessor.estimate_reading_time(word_count),
                        'difficulty_score': PDFProcessor.estimate_difficulty(full_text)
                    }
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'full_text': '',
                'statistics': {
                    'word_count': 0,
                    'char_count': 0,
                    'estimated_reading_time': 0,
                    'difficulty_score': 0.5
                }
            }
    
    @staticmethod
    def extract_text_from_bytes(file_bytes: bytes, filename: str) -> Dict[str, Any]:
        """
        Extract text content from PDF bytes
        
        Args:
            file_bytes: PDF file as bytes
            filename: Name of the file
            
        Returns:
            Dictionary containing extracted text and metadata
        """
        try:
            pdf_reader = PyPDF2.PdfReader(BytesIO(file_bytes))
            
            # Extract metadata
            metadata = {
                'total_pages': len(pdf_reader.pages),
                'filename': filename,
                'title': '',
                'author': '',
                'subject': ''
            }
            
            # Get document info if available
            if pdf_reader.metadata:
                metadata.update({
                    'title': pdf_reader.metadata.get('/Title', ''),
                    'author': pdf_reader.metadata.get('/Author', ''),
                    'subject': pdf_reader.metadata.get('/Subject', '')
                })
            
            # Extract text from all pages
            full_text = ""
            page_texts = []
            
            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    page_text = page.extract_text()
                    page_texts.append({
                        'page_number': page_num + 1,
                        'text': page_text,
                        'word_count': len(page_text.split()) if page_text else 0
                    })
                    full_text += page_text + "\n"
                except Exception as e:
                    print(f"Error extracting text from page {page_num + 1}: {e}")
                    page_texts.append({
                        'page_number': page_num + 1,
                        'text': '',
                        'word_count': 0,
                        'error': str(e)
                    })
            
            # Calculate statistics
            word_count = len(full_text.split()) if full_text else 0
            char_count = len(full_text)
            
            return {
                'success': True,
                'full_text': full_text,
                'page_texts': page_texts,
                'metadata': metadata,
                'statistics': {
                    'word_count': word_count,
                    'char_count': char_count,
                    'estimated_reading_time': PDFProcessor.estimate_reading_time(word_count),
                    'difficulty_score': PDFProcessor.estimate_difficulty(full_text)
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'full_text': '',
                'statistics': {
                    'word_count': 0,
                    'char_count': 0,
                    'estimated_reading_time': 0,
                    'difficulty_score': 0.5
                }
            }
    
    @staticmethod
    def estimate_reading_time(word_count: int, reading_speed: float = 200.0) -> float:
        """
        Estimate reading time in minutes based on word count
        
        Args:
            word_count: Number of words in the text
            reading_speed: Reading speed in words per minute (default: 200 WPM)
            
        Returns:
            Estimated reading time in minutes
        """
        if word_count <= 0:
            return 0.0
        return round(word_count / reading_speed, 2)
    
    @staticmethod
    def estimate_difficulty(text: str) -> float:
        """
        Estimate text difficulty based on various metrics
        
        Args:
            text: Text content to analyze
            
        Returns:
            Difficulty score between 0.0 and 1.0
        """
        if not text or len(text.strip()) == 0:
            return 0.5
        
        try:
            # Basic text analysis metrics
            sentences = re.split(r'[.!?]+', text)
            sentences = [s.strip() for s in sentences if s.strip()]
            words = text.split()
            
            if len(sentences) == 0 or len(words) == 0:
                return 0.5
            
            # Average sentence length
            avg_sentence_length = len(words) / len(sentences)
            
            # Average word length
            avg_word_length = sum(len(word) for word in words) / len(words)
            
            # Count of complex words (more than 6 characters)
            complex_words = [word for word in words if len(word) > 6]
            complex_word_ratio = len(complex_words) / len(words)
            
            # Flesch Reading Ease approximation
            # Higher values = easier text
            flesch_score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * (sum(PDFProcessor._count_syllables(word) for word in words) / len(words)))
            
            # Convert to difficulty score (0.0 = easy, 1.0 = very difficult)
            if flesch_score >= 90:
                difficulty = 0.1  # Very easy
            elif flesch_score >= 80:
                difficulty = 0.2  # Easy
            elif flesch_score >= 70:
                difficulty = 0.3  # Fairly easy
            elif flesch_score >= 60:
                difficulty = 0.4  # Standard
            elif flesch_score >= 50:
                difficulty = 0.5  # Fairly difficult
            elif flesch_score >= 30:
                difficulty = 0.7  # Difficult
            else:
                difficulty = 0.9  # Very difficult
            
            # Adjust based on other factors
            if complex_word_ratio > 0.3:
                difficulty += 0.1
            if avg_word_length > 7:
                difficulty += 0.1
            
            # Ensure score is between 0.0 and 1.0
            return min(max(difficulty, 0.0), 1.0)
            
        except Exception as e:
            print(f"Error calculating difficulty: {e}")
            return 0.5
    
    @staticmethod
    def _count_syllables(word: str) -> int:
        """
        Estimate syllable count in a word
        
        Args:
            word: Word to count syllables for
            
        Returns:
            Estimated number of syllables
        """
        word = word.lower()
        vowels = "aeiouy"
        syllable_count = 0
        previous_was_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not previous_was_vowel:
                syllable_count += 1
            previous_was_vowel = is_vowel
        
        # Handle silent 'e'
        if word.endswith('e'):
            syllable_count -= 1
        
        # Every word has at least one syllable
        return max(syllable_count, 1)
    
    @staticmethod
    def extract_sections(text: str, max_section_words: int = 500) -> List[Dict[str, Any]]:
        """
        Split text into manageable sections for study scheduling
        
        Args:
            text: Full text content
            max_section_words: Maximum words per section
            
        Returns:
            List of text sections with metadata
        """
        if not text or len(text.strip()) == 0:
            return []
        
        try:
            # Split by paragraphs first
            paragraphs = text.split('\n\n')
            sections = []
            current_section = ""
            current_word_count = 0
            section_number = 1
            
            for paragraph in paragraphs:
                paragraph = paragraph.strip()
                if not paragraph:
                    continue
                
                para_words = len(paragraph.split())
                
                # If adding this paragraph would exceed the limit, start new section
                if current_word_count + para_words > max_section_words and current_section:
                    sections.append({
                        'section_number': section_number,
                        'text': current_section.strip(),
                        'word_count': current_word_count,
                        'estimated_reading_time': PDFProcessor.estimate_reading_time(current_word_count)
                    })
                    current_section = paragraph
                    current_word_count = para_words
                    section_number += 1
                else:
                    current_section += "\n\n" + paragraph if current_section else paragraph
                    current_word_count += para_words
            
            # Add the last section if it has content
            if current_section.strip():
                sections.append({
                    'section_number': section_number,
                    'text': current_section.strip(),
                    'word_count': current_word_count,
                    'estimated_reading_time': PDFProcessor.estimate_reading_time(current_word_count)
                })
            
            return sections
            
        except Exception as e:
            print(f"Error extracting sections: {e}")
            return [{
                'section_number': 1,
                'text': text,
                'word_count': len(text.split()),
                'estimated_reading_time': PDFProcessor.estimate_reading_time(len(text.split()))
            }]
