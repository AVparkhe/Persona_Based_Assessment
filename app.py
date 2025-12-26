from flask import Flask, render_template, request, jsonify, session
from flask_session import Session
from conversation_controller import ConversationController
import os
import uuid

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "super_secret_dev_key")
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_PERMANENT"] = False

# Initialize Flask-Session
Session(app)

@app.route("/")
def home():
    # Clear session on load/reload for fresh start in this simple version
    session.clear()
    session["conversation_id"] = str(uuid.uuid4())
    # Initialize basic state
    session["history"] = []
    session["state"] = "IDLE"
    return render_template("index.html")

@app.route("/api/start", methods=["POST"])
def start_chat():
    controller = ConversationController()
    response = controller.start_conversation()
    
    # Save state to session
    session["history"] = controller.history
    session["state"] = controller.state
    # Save persona engine state
    session["persona_engine_state"] = controller.persona_engine.to_dict()
    
    return jsonify({"message": response, "history": session["history"]})

@app.route("/api/chat", methods=["POST"])
def chat():
    if not session.get("conversation_id"):
        return jsonify({"error": "No active session"}), 400

    data = request.json
    user_input = data.get("message", "")
    
    # Rehydrate controller from session
    # Pass the saved persona_engine_state if it exists
    persona_state = session.get("persona_engine_state")
    controller = ConversationController(persona_engine_state=persona_state)
    
    controller.history = session.get("history", [])
    controller.state = session.get("state", "IDLE")
    
    response = controller.handle_response(user_input)
    
    # Save state back to session
    session["history"] = controller.history
    session["state"] = controller.state
    session["persona_engine_state"] = controller.persona_engine.to_dict()
    
    return jsonify({"message": response, "history": session["history"]})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
