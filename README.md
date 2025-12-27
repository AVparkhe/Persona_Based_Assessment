# Persona-Based Conversational Assessment System

An intelligent, adaptive assessment platform that evaluates candidates through natural, interview-style conversations. Driven by **Groq** (using Llama 3 or similar models) and advanced prompt engineering, this system replaces static MCQs with dynamic interactions to assess Logical Thinking, Communication Skills, and Adaptability.

---

## 🚀 Features

*   **Conversational Interface:** Conducts assessments via a chat interface, mimicking a real human interviewer.
*   **Adaptive Questioning:** Dynamically adjusts the difficulty and focus of questions based on the candidate's responses.
*   **Persona-Driven Logic:** Utilizes strict prompt engineering to maintain a consistent, professional, and fair interviewer persona.
*   **Context Awareness:** Remembers previous interactions and candidate background to ask relevant follow-up questions.
*   **Multi-Dimensional Evaluation:** Assesses candidates on logic, communication, and adaptability rather than just factual recall.

## 🛠️ Tech Stack

*   **Language:** Python 3.12+
*   **Framework:** Flask (Web Server)
*   **AI Engine:** Groq (Llama 3 70B via `groq` library)
*   **Session Management:** Flask-Session (Filesystem-based)
*   **Frontend:** HTML/CSS/JavaScript (Simple Chat UI)

## 📂 Project Structure

```
├── app.py                  # Main Flask application entry point
├── conversation_controller.py # Manages the flow of the conversation
├── persona_engine.py       # Handles persona profiling and state
├── groq_client.py          # Interface for Groq API
├── prompts.py              # Centralized repository for system prompts
├── requirements.txt        # Python dependencies
└── templates/
    └── index.html          # Chat interface frontend
```

## ⚙️ Installation & Setup

1.  **Clone the Repository**
    ```bash
    git clone <repository-url>
    cd Persona_Based_Assessment
    ```

2.  **Create a Virtual Environment (Recommended)**
    ```bash
    python -m venv .venv
    # Windows
    .venv\Scripts\activate
    # macOS/Linux
    source .venv/bin/activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configuration**
    *   You need a Groq API Key.
    *   Set the `GROQ_API_KEY` environment variable. You can do this in your terminal or create a `.env` file (if you add `python-dotenv` support, otherwise set it in your system environment).
    *   *Note: The current code may look for the key in environment variables directly.*

    ```bash
    # Example (Windows PowerShell)
    $env:GROQ_API_KEY="your_api_key_here"
    ```

5.  **Run the Application**
    ```bash
    python app.py
    ```

6.  **Access the Interface**
    Open your browser and navigate to:
    `http://127.0.0.1:5000`

## 🧩 How It Works

1.  **Initialization:** The user lands on the chat interface.
2.  **Start:** The `ConversationController` initializes a session and triggers the `PersonaEngine`.
3.  **Interaction:**
    *   User inputs are sent to the backend.
    *   The `GroqClient` generates a response based on the current context and the specific prompt for that stage of the interview.
    *   The system maintains state (history, current topic, difficulty) to ensure continuity.
4.  **Assessment:** The system evaluates responses in the background (or post-interaction) to determine the candidate's proficiency.

## 📄 License

[MIT License](LICENSE)
