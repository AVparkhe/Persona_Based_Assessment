from persona_engine import PersonaEngine
from gemini_client import GeminiClient
from prompts import QUESTION_GENERATION_PROMPT, INTERVIEWER_PERSONA_PROMPT, RESPONSE_ANALYSIS_PROMPT

class ConversationController:
    """
    Manages the state and flow of the conversation.
    Acts as the State Machine described in the architecture.
    """
    def __init__(self, persona_engine_state=None):
        self.state = "IDLE"  # IDLE, PROFILING, ACTIVE, ENDED
        self.history = []
        self.persona_engine = PersonaEngine(state_dict=persona_engine_state)
        self.gemini_client = GeminiClient()
        self.question_count = 0 
        
        # State tracking for adaptive logic
        self.current_difficulty = "Medium"
        self.observed_strengths = []
        self.observed_weaknesses = []
        self.latest_analysis = {}

    def start_conversation(self):
        """Initializes the conversation and starts profiling."""
        self.state = "PROFILING"
        # Start with the first profiling question
        first_q = self.persona_engine.get_next_question()
        welcome_message = f"Hello! I am your AI Interviewer. To tailor this assessment for you, I need to ask a few setting-the-stage questions.\n\n{first_q}"
        
        self.history.append({"role": "system", "content": welcome_message})
        return welcome_message

    def handle_response(self, user_input):
        """
        Process user input through the state machine.
        """
        if self.state == "ENDED":
            return "The conversation has ended. Please refresh to start a new assessment."
            
        self.history.append({"role": "user", "content": user_input})
        
        if user_input.lower() in ["bye", "exit", "quit"]:
            return self.end_conversation()

        if self.state == "PROFILING":
            return self._handle_profiling(user_input)
        
        if self.state == "ACTIVE":
            return self._handle_active_interview(user_input)

        return "Error: Unknown State"

    def _handle_profiling(self, user_input):
        """Handles the initial set of questions to build the user profile."""
        # Process the answer to the current question
        self.persona_engine.process_answer(user_input)
        
        # Check if profiling is done
        if self.persona_engine.profiling_complete:
            self.state = "ACTIVE"
            self.question_count = 1
            
            # Transition to the actual interview
            # Generate the first question using the Initial Persona Prompt or Question Generator
            # We'll use the Question Generator with a "start" signal for consistency
            
            persona_data = self.persona_engine.profile['assigned_persona']
            candidate_name = self.persona_engine.profile.get('candidate_name', 'Candidate')
            background = f"{self.persona_engine.profile.get('role_focus')} with {self.persona_engine.profile.get('years_experience')} years experience"
            
            # Set initial difficulty from persona
            self.current_difficulty = persona_data.get('starting_difficulty', 'Medium')
            
            # Initial Context for First Question
            context = {
                "persona_name": persona_data.get('persona_name', 'Interviewer'),
                "target_users": persona_data.get('target_users', 'Candidates'),
                "education": persona_data.get('background_assumptions', {}).get('education', 'N/A'),
                "experience_level": persona_data.get('background_assumptions', {}).get('experience_level', 'N/A'),
                "domain_exposure": persona_data.get('background_assumptions', {}).get('domain_exposure', 'N/A'),
                "expected_skills": ", ".join(persona_data.get('what_persona_should_be_good_at', [])),
                "struggles": ", ".join(persona_data.get('what_persona_may_struggle_with', [])),
                "start_difficulty": persona_data.get('difficulty_level', {}).get('start_level', 'Medium'),
                "max_difficulty": persona_data.get('difficulty_level', {}).get('max_level', 'Hard'),
                "target_dimension": "Logical Thinking", # Start with Logical Thinking
                "last_answer": "I am ready to begin.", 
                "strengths": "Not yet observed",
                "weaknesses": "Not yet observed",
                "difficulty": self.current_difficulty,
                "adaptive_instruction": "Start with a simple question relevant to the persona."
            }
            
            # Generate first question
            first_interview_question = self.gemini_client.generate_content(QUESTION_GENERATION_PROMPT, context)
            
            transition_msg = (
                f"Thank you, {candidate_name}. Based on your profile, I will be conducting a {persona_data['title']} interview.\n"
                f"Let's begin.\n\n"
                f"{first_interview_question}"
            )
            self.history.append({"role": "system", "content": transition_msg})
            return transition_msg
        else:
            # Get the next profiling question
            next_q = self.persona_engine.get_next_question()
            self.history.append({"role": "system", "content": next_q})
            return next_q

    def _handle_active_interview(self, user_input):
        """Generates the next question using Gemini after analyzing the response."""
        
        persona_data = self.persona_engine.profile['assigned_persona']
        last_system_message = self.history[-2]['content'] if len(self.history) >= 2 else "Start of Interview"
        
        # --- PHASE 4: Response Analysis ---
        analysis_context = {
            "persona_name": f"{persona_data['title']} ({persona_data['tone']})",
            "difficulty": self.current_difficulty,
            "last_question": last_system_message,
            "user_response": user_input
        }
        
        # Analyze the user's response
        analysis_result = self.gemini_client.generate_json(RESPONSE_ANALYSIS_PROMPT, analysis_context)
        
        adaptive_instruction = "Continue with the interview flow."
        should_advance_topic = True

        if analysis_result:
            self.latest_analysis = analysis_result
            # Aggregate strengths and weaknesses
            if "observed_strengths" in analysis_result:
                self.observed_strengths.extend(analysis_result["observed_strengths"])
            if "observed_weaknesses" in analysis_result:
                self.observed_weaknesses.extend(analysis_result["observed_weaknesses"])
                
            # --- PHASE 5: Adaptive Logic ---
            action = analysis_result.get("suggested_action", "maintain_difficulty")
            
            if action == "increase_difficulty":
                self.current_difficulty = "Hard" if self.current_difficulty == "Medium" else "Medium"
                adaptive_instruction = "Candidate is doing well. Increase complexity or add constraints."
                should_advance_topic = True
                
            elif action == "decrease_difficulty":
                self.current_difficulty = "Easy" if self.current_difficulty == "Medium" else "Medium"
                adaptive_instruction = "Candidate is struggling. Simplify the question or guide them."
                should_advance_topic = True # Advance, but make it easier
            
            elif action == "probe_deeper":
                # Do NOT advance the topic controller; stay on the same dimension/topic
                should_advance_topic = False
                adaptive_instruction = "Candidate's answer was surface level or vague. Ask a follow-up question to dig deeper into the SAME topic. Do not switch topics yet."

        # --- Generate Next Question ---
        
        # Only move to next dimension/question # if we aren't probing deeper
        if should_advance_topic:
            self.question_count += 1
            
        # Check if we have reached the limit (Hybrid approach: 5 questions)
        if self.question_count > 5:
             return self.end_conversation()
        
        # Simple Logic to rotate dimensions
        dimensions = ["Logical Thinking", "Communication", "Adaptability"]
        # If we didn't advance, we use the same index associated with the previous question
        current_dim_index = self.question_count if should_advance_topic else (self.question_count)
        target_dim = dimensions[current_dim_index % 3]
        
        context = {
            "persona_name": persona_data.get('persona_name', 'Interviewer'),
            "target_users": persona_data.get('target_users', 'Candidates'),
            "expected_skills": ", ".join(persona_data.get('what_persona_should_be_good_at', [])),
            "struggles": ", ".join(persona_data.get('what_persona_may_struggle_with', [])),
            "start_difficulty": persona_data.get('difficulty_level', {}).get('start_level', 'Medium'),
            "target_dimension": target_dim,
            "last_answer": user_input,
            "strengths": ", ".join(list(set(self.observed_strengths))[:3]) or "None yet", # Limit to top 3 unique
            "weaknesses": ", ".join(list(set(self.observed_weaknesses))[:3]) or "None yet",
            "difficulty": self.current_difficulty,
            "adaptive_instruction": adaptive_instruction
        }
        
        next_question = self.gemini_client.generate_content(QUESTION_GENERATION_PROMPT, context)
        
        self.history.append({"role": "system", "content": next_question})
        return next_question

    def end_conversation(self):
        """Ends the conversation and generates the final report."""
        self.state = "ENDED"
        
        closing_message = "Thank you for your time. The assessment is complete. Generating your feedback report..."
        self.history.append({"role": "system", "content": closing_message})
        
        # --- PHASE 6: Result Generation ---
        try:
            persona_data = self.persona_engine.profile.get('assigned_persona', {})
            candidate_name = self.persona_engine.profile.get('candidate_name', 'Candidate')
            background = f"{self.persona_engine.profile.get('role_focus', 'N/A')} with {self.persona_engine.profile.get('years_experience', 'N/A')} years"
            
            # Convert history to a readable transcript string
            transcript = ""
            for msg in self.history:
                role = "Interviewer" if msg['role'] == "system" else "Candidate"
                transcript += f"{role}: {msg['content']}\n\n"
            
            context = {
                "candidate_name": candidate_name,
                "persona_name": f"{persona_data.get('title', 'Interviewer')} ({persona_data.get('tone', 'Neutral')})",
                "background": background,
                "full_conversation": transcript
            }
            
            from prompts import RESULT_GENERATION_PROMPT
            report_json = self.gemini_client.generate_json(RESULT_GENERATION_PROMPT, context)
            
            self.report = report_json # Store report in controller state
            
            # Format a simple text summary to append to the chat
            if report_json:
                summary_text = (
                    f"\n\n--- ASSESSMENT REPORT ---\n"
                    f"**Summary**: {report_json.get('profile_summary', 'N/A')}\n\n"
                    f"**Strengths**: {', '.join(report_json.get('strengths', []))}\n"
                    f"**Areas for Improvement**: {', '.join(report_json.get('improvement_areas', []))}\n"
                    f"**Overall Recommendation**: {report_json.get('overall_recommendation', 'N/A')}"
                )
                self.history.append({"role": "system", "content": summary_text})
                return closing_message + summary_text
                
        except Exception as e:
            print(f"Error generating report: {e}")
            return closing_message + "\n(Report generation failed due to an error)."

        return closing_message
