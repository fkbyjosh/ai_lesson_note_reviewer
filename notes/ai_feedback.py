from logging import config
import google.generativeai as genai
from django.conf import settings
from typing import Dict, Any
import json
import re

GEMINI_API_KEY = config('GEMINI_API_KEY')

class AIFeedbackGenerator:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-1.5-flash')  # Free tier model
        
    def generate_feedback(self, lesson_note) -> Dict[str, Any]:
        """
        Generate AI feedback for a lesson note
        Returns: {
            'feedback_text': str,
            'score': int (1-100),
            'suggestions': list,
            'strengths': list
        }
        """
        try:
            prompt = self._create_prompt(lesson_note)
            
            #configure generation settings for better JSON output
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
            
            #extract JSON from response
            feedback_data = self._extract_json_from_response(response.text)
            return self._validate_feedback(feedback_data)
            
        except Exception as e:
            # Log the error in production
            print(f"AI Feedback Error: {str(e)}")
            return self._get_fallback_feedback()
    
    def _extract_json_from_response(self, response_text: str) -> Dict[str, Any]:
        """Extract JSON from Gemini response text"""
        try:
            #find JSON block in response
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            
            #try to find JSON without code blocks
            json_match = re.search(r'(\{.*?\})', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            
            #if no JSON found, create structure from text
            return self._parse_text_response(response_text)
            
        except json.JSONDecodeError:
            return self._parse_text_response(response_text)
    
    def _parse_text_response(self, text: str) -> Dict[str, Any]:
        """Parse text response into structured format"""
        # Extract score if present
        score_match = re.search(r'score[:\s]+(\d+)', text, re.IGNORECASE)
        score = int(score_match.group(1)) if score_match else 75
        
        return {
            'feedback_text': text[:500],  # Truncate if too long
            'score': min(max(score, 1), 100),
            'strengths': ['Lesson structure is clear'],
            'suggestions': ['Consider adding more interactive elements'],
            'areas_for_improvement': ['Assessment methods could be enhanced'],
            'overall_assessment': 'Good lesson plan with room for improvement'
        }
    
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
        
        Please ensure your response is in valid JSON format.
        """
    
    def _validate_feedback(self, feedback_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and sanitize AI response"""
        validated = {
            'feedback_text': feedback_data.get('feedback_text', 'No feedback provided'),
            'score': min(max(int(feedback_data.get('score', 70)), 1), 100),
            'strengths': feedback_data.get('strengths', [])[:5],  # Limit to 5 items
            'suggestions': feedback_data.get('suggestions', [])[:5],
            'areas_for_improvement': feedback_data.get('areas_for_improvement', [])[:5],
            'overall_assessment': feedback_data.get('overall_assessment', 'Assessment not provided')
        }
        return validated
    
    def _get_fallback_feedback(self) -> Dict[str, Any]:
        """Fallback feedback if AI fails"""
        return {
            'feedback_text': 'AI feedback temporarily unavailable. Please try again later or contact support.',
            'score': 70,
            'strengths': ['Lesson successfully submitted for review'],
            'suggestions': ['Please resubmit for detailed AI feedback'],
            'areas_for_improvement': ['AI analysis pending - will be available shortly'],
            'overall_assessment': 'Awaiting AI review - technical issue resolved soon'
        }