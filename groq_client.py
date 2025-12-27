import os
import json
import time
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

class GroqClient:
    """
    Wrapper for Groq API to handle prompt execution, replacing GeminiClient.
    """
    def __init__(self):
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            print("Warning: GROQ_API_KEY not found in environment variables.")
            self.client = None
        else:
            self.client = Groq(api_key=api_key)
            
        # Using a reliable Groq model
        self.model_name = "llama-3.3-70b-versatile"

    def generate_content(self, prompt, context_vars=None):
        """
        Substitutes variables into the prompt and calls the Groq API.
        
        Args:
            prompt (str): The raw prompt template.
            context_vars (dict): Dictionary of variables to replace in the template.
            
        Returns:
            str: The generated text response.
        """
        if not self.client:
            return "Error: GROQ_API_KEY not configured."

        if context_vars:
            for key, value in context_vars.items():
                prompt = prompt.replace(f"{{{{{key}}}}}", str(value))
        
        # Retry loop for rate limits or transient errors
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                chat_completion = self.client.chat.completions.create(
                    messages=[
                        {
                            "role": "user",
                            "content": prompt,
                        }
                    ],
                    model=self.model_name,
                    temperature=0.7,
                )
                return chat_completion.choices[0].message.content.strip()

            except Exception as e:
                error_str = str(e)
                print(f"Groq API Error (Attempt {attempt+1}/{max_retries}): {error_str}")
                
                # specific rate limit handling could go here
                if attempt < max_retries - 1:
                    time.sleep(2 * (attempt + 1))
                    continue
                
                return f"DEBUG ERROR: {error_str}"

    def generate_json(self, prompt, context_vars=None):
        """
        Generates content and attempts to parse it as JSON.
        Useful for Evaluation and Result Generation.
        """
        if not self.client:
            return {{}}

        # Append instructions to ensure JSON output if not already present in prompt
        json_instruction = "\n\nIMPORTANT: Output ONLY valid JSON code. Do not wrap in markdown blocks like ```json."
        if "JSON" not in prompt:
            prompt += json_instruction
            
        text_response = self.generate_content(prompt, context_vars)
        
        # Strip markdown code blocks if present (common with LLMs)
        if text_response.startswith("```json"):
            text_response = text_response[7:]
        if text_response.startswith("```"):
            text_response = text_response[3:]
        if text_response.endswith("```"):
            text_response = text_response[:-3]
            
        try:
            return json.loads(text_response.strip())
        except json.JSONDecodeError:
            print(f"JSON Parse Error. Raw output: {text_response}")
            # Simple retry or fallback logic could be added here
            return {{}}
