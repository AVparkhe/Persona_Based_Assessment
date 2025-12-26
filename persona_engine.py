class PersonaEngine:
    """
    Handles the profiling and persona assignment logic.
    Decides the 'character' of the interviewer and the context of the assessment.
    """
    def __init__(self, state_dict=None):
        self.profile = {}
        self.profiling_complete = False
        self.current_step = 0
        self.profiling_questions = [
            {
                "id": "name",
                "text": "Before we begin, could you please tell me your full name?",
                "field": "candidate_name"
            },
            {
                "id": "role",
                "text": "What specific role or technology stack are you being assessed for today? (e.g., Python Backend, Frontend React, DevOps)",
                "field": "role_focus"
            },
            {
                "id": "experience",
                "text": "How many years of professional experience do you have in this field?",
                "field": "years_experience"
            }
        ]
        
        if state_dict:
            self.from_dict(state_dict)

    def to_dict(self):
        """Serializes the engine state to a dictionary."""
        return {
            "profile": self.profile,
            "profiling_complete": self.profiling_complete,
            "current_step": self.current_step
        }

    def from_dict(self, data):
        """Restores the engine state from a dictionary."""
        self.profile = data.get("profile", {})
        self.profiling_complete = data.get("profiling_complete", False)
        self.current_step = data.get("current_step", 0)

    def get_next_question(self):
        """Returns the next profiling question or None if complete."""
        if self.current_step < len(self.profiling_questions):
            return self.profiling_questions[self.current_step]["text"]
        return None

    def process_answer(self, answer):
        """Stores the answer and advances the step."""
        if self.current_step < len(self.profiling_questions):
            current_field = self.profiling_questions[self.current_step]["field"]
            self.profile[current_field] = answer
            self.current_step += 1
            
            if self.current_step >= len(self.profiling_questions):
                self.profiling_complete = True
                self.assign_persona()
                
            return True
        return False

    def assign_persona(self):
        """
        Rule-based logic to assign an interviewer persona based on the profile.
        """
        role = self.profile.get("role_focus", "").lower()
        years = self.profile.get("years_experience", "0")
        
        # Simple heuristic for parsing years (very basic for now)
        try:
            years_int = int(''.join(filter(str.isdigit, years)))
        except ValueError:
            years_int = 0

        # Determine Seniority & Base Profile
        if years_int > 5:
            experience_level = "Experienced"
            seniority = "Senior"
            tone = "peer-to-peer, architectural, high-level"
            difficulty_start = "Hard"
            behavioral_focus = ["Leadership", "System Design", "Mentorship"]
        elif years_int > 2:
            experience_level = "Mid-Level"
            seniority = "Mid-Level"
            tone = "practical, hands-on, balanced"
            difficulty_start = "Medium"
            behavioral_focus = ["Problem Solving", "Code Quality", "Collaboration"]
        else:
            experience_level = "Fresher"
            seniority = "Junior"
            tone = "mentorship, fundamental, encouraging"
            difficulty_start = "Easy"
            behavioral_focus = ["Curiosity", "Logic", "Learning Agility"]

        # Determine Domain & Skills
        if "python" in role or "backend" in role or "django" in role or "flask" in role:
            domain = "Backend Engineering"
            expected_skills = ["Data Structures", "Algorithms", "Database Design"]
            struggles = ["System Design", "Scalability", "Microservices"]
            educational_background = "Computer Science or related field"
        elif "react" in role or "frontend" in role or "javascript" in role or "css" in role:
            domain = "Frontend Engineering"
            expected_skills = ["UI/UX Principles", "JavaScript/TypeScript", "State Management"]
            struggles = ["Performance Optimization", "Webpack/Build Tools", "Security"]
            educational_background = "Computer Science, Design, or self-taught portfolio"
        elif "devops" in role or "cloud" in role or "aws" in role:
            domain = "DevOps & Infrastructure"
            expected_skills = ["CI/CD", "Cloud Services (AWS/Azure)", "Infrastructure as Code"]
            struggles = ["Complex Networking", "Security Compliance", "Cost Optimization"]
            educational_background = "Engineering or IT Certifications"
        else:
            domain = "General Software Engineering"
            expected_skills = ["Programming Fundamentals", "Problem Solving", "Debugging"]
            struggles = ["Complex Logic", "Design Patterns", "Testing"]
            educational_background = "STEM degree or relevant experience"

        self.profile["assigned_persona"] = {
            "persona_name": f"{seniority} {domain} Interviewer",
            "target_users": f"Candidates aiming for {seniority} {domain} roles",
            "background_assumptions": {
                "education": educational_background,
                "experience_level": experience_level,
                "domain_exposure": domain
            },
            "what_persona_should_be_good_at": expected_skills,
            "what_persona_may_struggle_with": struggles,
            "assessment_focus": {
                "dimension_1": "Logical Thinking",
                "dimension_2": "Communication",
                "dimension_3": "Adaptability"
            },
            "difficulty_level": {
                "start_level": difficulty_start,
                "max_level": "Hard" 
            },
            # Keep legacy fields for compatibility with existing prompts/controller until fully migrated
            "title": f"{seniority} {domain} Interviewer",
            "tone": tone,
            "philosophy": "Reasoning over syntax. Ask 'why' more than 'how'.",
            "starting_difficulty": difficulty_start,
            "expected_skills": expected_skills,
            "behavioral_traits": behavioral_focus
        }

    def get_persona_context(self):
        """Returns the text description of the assigned persona."""
        if not self.profiling_complete:
            return None
        
        p = self.profile["assigned_persona"]
        return f"You are a {p['title']}. Your tone is {p['tone']}. Your philosophy is: {p['philosophy']}."
