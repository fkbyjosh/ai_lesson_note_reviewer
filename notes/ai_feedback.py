import google.generativeai as genai
from django.conf import settings
from typing import Dict, Any
import json
import re
from decouple import config

GEMINI_API_KEY = config('GEMINI_API_KEY')

class AIFeedbackGenerator:
    def __init__(self):
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        
    def generate_feedback(self, lesson_note) -> Dict[str, Any]:
        """
        Generate AI feedback for a lesson note
        Returns structured feedback matching the frontend expectations:
        {
            'feedback_text': str,
            'score': int (1-100),
            'strengths': list,
            'suggestions': list,
            'areas_for_improvement': list,
            'overall_assessment': str
        }
        """
        try:
            prompt = self._create_prompt(lesson_note)
            
            # Configure generation settings for better JSON output
            generation_config = genai.types.GenerationConfig(
                temperature=0.7,
                max_output_tokens=1500,
                top_p=0.9,
                top_k=40
            )
            
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            # Extract and validate JSON from response
            feedback_data = self._extract_json_from_response(response.text)
            return self._validate_and_structure_feedback(feedback_data)
            
        except Exception as e:
            # Log the error in production
            print(f"AI Feedback Error: {str(e)}")
            return self._get_fallback_feedback()
    
    def _extract_json_from_response(self, response_text: str) -> Dict[str, Any]:
        """Extract JSON from Gemini response text"""
        try:
            # Find JSON block in response
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            
            # Try to find JSON without code blocks
            json_match = re.search(r'(\{.*?\})', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            
            # If no JSON found, create structure from text
            return self._parse_text_response(response_text)
            
        except json.JSONDecodeError:
            return self._parse_text_response(response_text)
    
    def _parse_text_response(self, text: str) -> Dict[str, Any]:
        """Parse text response into structured format when JSON parsing fails"""
        # Extract score if present
        score_match = re.search(r'score[:\s]+(\d+)', text, re.IGNORECASE)
        score = int(score_match.group(1)) if score_match else 75
        
        # Extract strengths section
        strengths_match = re.search(r'strengths?[:\s]+(.*?)(?=suggestions?|areas?|overall|$)', text, re.IGNORECASE | re.DOTALL)
        strengths = self._extract_list_items(strengths_match.group(1)) if strengths_match else ['Lesson structure is clear']
        
        # Extract suggestions section
        suggestions_match = re.search(r'suggestions?[:\s]+(.*?)(?=strengths?|areas?|overall|$)', text, re.IGNORECASE | re.DOTALL)
        suggestions = self._extract_list_items(suggestions_match.group(1)) if suggestions_match else ['Consider adding more interactive elements']
        
        # Extract areas for improvement
        areas_match = re.search(r'areas?.*?improvement[:\s]+(.*?)(?=strengths?|suggestions?|overall|$)', text, re.IGNORECASE | re.DOTALL)
        areas = self._extract_list_items(areas_match.group(1)) if areas_match else ['Assessment methods could be enhanced']
        
        return {
            'feedback_text': text[:500],  # Truncate if too long
            'score': min(max(score, 1), 100),
            'strengths': strengths,
            'suggestions': suggestions,
            'areas_for_improvement': areas,
            'overall_assessment': 'Good lesson plan with room for improvement'
        }
    
    def _extract_list_items(self, text: str) -> list:
        """Extract list items from text"""
        items = []
        # Look for bullet points or numbered lists
        lines = text.strip().split('\n')
        for line in lines:
            line = line.strip()
            if line and (line.startswith('•') or line.startswith('-') or line.startswith('*') or re.match(r'^\d+\.', line)):
                clean_item = re.sub(r'^[•\-\*\d\.\s]+', '', line).strip()
                if clean_item:
                    items.append(clean_item)
        return items[:5]  # Limit to 5 items
    
    def _create_prompt(self, lesson_note) -> str:
        """Create a structured prompt for Gemini AI"""
        return f"""
        You are an experienced educational reviewer specializing in lesson plan evaluation. 
        Please review this lesson note and provide detailed feedback.

        **Lesson Details:**
        - Subject: {lesson_note.subject}
        - Grade Level: {lesson_note.grade_level}
        - Term: {lesson_note.term}
        - Teacher: {lesson_note.teacher.name}
        
        **Lesson Content:**
        {lesson_note.content}
        
        **Please provide your response in JSON format with the following structure:**
        
        ```json
        {{
            "feedback_text": "Detailed constructive feedback paragraph explaining strengths and areas for improvement",
            "score": 85,
            "strengths": ["specific strength 1", "specific strength 2", "specific strength 3"],
            "suggestions": ["actionable suggestion 1", "actionable suggestion 2", "actionable suggestion 3"],
            "areas_for_improvement": ["specific area 1", "specific area 2"],
            "overall_assessment": "Brief overall assessment of the lesson plan"
        }}
        ```
        
        **Evaluation Criteria:**
        - Learning objectives clarity and alignment (20%)
        - Content accuracy and age-appropriateness (25%)
        - Teaching methodology and pedagogy (20%)
        - Assessment methods and strategies (15%)
        - Student engagement and interaction (10%)
        - Differentiation and inclusivity (10%)
        
        **Guidelines:**
        - Score should be between 1-100
        - Be constructive and specific in your feedback
        - Provide actionable suggestions
        - Consider the grade level and subject context
        - Focus on educational best practices
        - Ensure all arrays contain at least 2-3 items
        
        Please ensure your response is in valid JSON format.
        """
    
    def _validate_and_structure_feedback(self, feedback_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and structure AI response to match frontend expectations exactly
        """
        # Ensure all required fields exist with proper defaults
        structured_feedback = {
            'feedback_text': str(feedback_data.get('feedback_text', 'No feedback provided')),
            'score': min(max(int(feedback_data.get('score', 70)), 1), 100),
            'strengths': self._ensure_list_format(feedback_data.get('strengths', [])),
            'suggestions': self._ensure_list_format(feedback_data.get('suggestions', [])),
            'areas_for_improvement': self._ensure_list_format(feedback_data.get('areas_for_improvement', [])),
            'overall_assessment': str(feedback_data.get('overall_assessment', 'Assessment not provided'))
        }
        
        # Ensure minimum items in each list
        if not structured_feedback['strengths']:
            structured_feedback['strengths'] = ['Lesson shows good structure and organization']
        
        if not structured_feedback['suggestions']:
            structured_feedback['suggestions'] = ['Consider adding more interactive elements', 'Include varied assessment methods']
        
        if not structured_feedback['areas_for_improvement']:
            structured_feedback['areas_for_improvement'] = ['Could benefit from more detailed learning objectives']
        
        return structured_feedback
    
    def _ensure_list_format(self, data) -> list:
        """Ensure data is in list format and properly formatted"""
        if isinstance(data, list):
            return [str(item).strip() for item in data if str(item).strip()][:5]  # Limit to 5 items
        elif isinstance(data, str):
            # Try to split string into list items
            items = [item.strip() for item in data.split('\n') if item.strip()]
            return items[:5]
        else:
            return []
    
    def _get_fallback_feedback(self) -> Dict[str, Any]:
        """
        Fallback feedback if AI fails - matches exact frontend structure
        """
        return {
            'feedback_text': 'AI feedback temporarily unavailable. Please try again later or contact support.',
            'score': 70,
            'strengths': [
                'Lesson successfully submitted for review',
                'Shows commitment to educational improvement'
            ],
            'suggestions': [
                'Please resubmit for detailed AI feedback',
                'Consider reviewing lesson structure while waiting'
            ],
            'areas_for_improvement': [
                'AI analysis pending - will be available shortly'
            ],
            'overall_assessment': 'Awaiting AI review - technical issue will be resolved soon'
        }