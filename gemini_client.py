import google.generativeai as genai
import os
import json
from dotenv import load_dotenv

load_dotenv()

class GeminiClient:
    """
    Wrapper for Google's Gemini API to handle prompt execution.
    """
    def __init__(self):
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            # Fallback or error logging can go here.
            # In production, we'd raise an error.
            print("Warning: GEMINI_API_KEY not found in environment variables.")
        else:
            genai.configure(api_key=api_key)
            
        # Using gemini-1.5-flash per user request
        self.model = genai.GenerativeModel('gemini-1.5-flash-001')

    def generate_content(self, prompt, context_vars=None):
        """
        Substitutes variables into the prompt and calls the Gemini API.
        
        Args:
            prompt (str): The raw prompt template.
            context_vars (dict): Dictionary of variables to replace in the template.
            
        Returns:
            str: The generated text response.
        """
        if context_vars:
            for key, value in context_vars.items():
                prompt = prompt.replace(f"{{{{{key}}}}}", str(value))
        
        # Retry loop for 429 Rate Limit
        max_retries = 5
        import time
        import re
        
        for attempt in range(max_retries):
            try:
                # Disable safety settings for interview context if needed, but default is usually fine.
                response = self.model.generate_content(prompt)
                return response.text.strip()
            except Exception as e:
                error_str = str(e)
                # Check for 429 error
                if "429" in error_str:
                    if attempt < max_retries - 1:
                        # Try to parse wait time from error message
                        wait_match = re.search(r'retry in (\d+(\.\d+)?)s', error_str)
                        if wait_match:
                            wait_time = float(wait_match.group(1)) + 1 # Add 1s buffer
                        else:
                            wait_time = (attempt + 1) * 5  # Fallback backoff: 5, 10, 15...
                        
                        print(f"Rate limit hit. Retrying in {wait_time:.1f} seconds...")
                        time.sleep(wait_time)
                        continue
                
                # If not 429 or retries exhausted:
                error_msg = f"Gemini API Error: {error_str}\n"
                print(error_msg)
                # Keep error silent in UI but log it
                return f"DEBUG ERROR: {error_str}"

    def generate_json(self, prompt, context_vars=None):
        """
        Generates content and attempts to parse it as JSON.
        Useful for Evaluation and Result Generation.
        """
        text_response = self.generate_content(prompt, context_vars)
        
        # Strip markdown code blocks if present
        if text_response.startswith("```json"):
            text_response = text_response[7:]
        if text_response.startswith("```"): # Sometimes it's just ```
            text_response = text_response[3:]
        if text_response.endswith("```"):
            text_response = text_response[:-3]
            
        try:
            return json.loads(text_response.strip())
        except json.JSONDecodeError:
            print(f"JSON Parse Error. Raw output: {text_response}")
            return {}
