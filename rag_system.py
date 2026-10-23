import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from google import genai

app = Flask(__name__)
# ✅ CRITICAL: Allows your GitHub Pages website to safely trigger this code
CORS(app)

GEMINI_API_KEY = "AQ.Ab8RN6JZ3xPjvjGMLphRoESsJfzt_I8T5BU1c4CfszlAiyA50w"
DOCS_FOLDER = "source_docs"

# Initialize the official Google GenAI Client
client = genai.Client(api_key=GEMINI_API_KEY)

def read_local_documents():
    """Reads all raw text files inside the cloud space folder automatically."""
    if not os.path.exists(DOCS_FOLDER):
        os.makedirs(DOCS_FOLDER)
        return ""

    combined_text = ""
    # Look for files within the repository directory
    if os.path.exists(DOCS_FOLDER):
        files = [f for f in os.listdir(DOCS_FOLDER) if f.endswith(".txt")]
        for filename in files:
            file_path = os.path.join(DOCS_FOLDER, filename)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    combined_text += f"\n--- DOCUMENT SOURCE: {filename} ---\n"
                    combined_text += f.read() + "\n"
            except Exception:
                pass
    return combined_text.strip()

@app.route("/", methods=["GET"])
def home():
    return "RAG Pipeline Backend Server is Online!", 200

@app.route("/api/chat", methods=["POST"])
def chat():
    # Capture the query sent from your frontend webpage
    data = request.json or {}
    user_query = data.get("query", "").strip()

    if not user_query:
        return jsonify({"error": "Query text is required"}), 400

    # 1. Gather all knowledge text data dynamically from the repository folder
    all_context = read_local_documents()
    
    if not all_context:
        all_context = 'The master control password for the D-Drive automated server cluster is "BlueSky-9942". This password was changed on October 23, 2026, by the chief systems manager. Do not share this information with unverified engineers.'

    # 2. Build the systemic RAG prompt layout matrix
    prompt = f"""You are a helpful AI assistant. Answer the user's question using ONLY the provided context blocks extracted from local documentation.
If the answer cannot be found in the context text, state clearly that you do not have that information.

LOCAL FILE DATA:
{all_context}

USER QUESTION:
{user_query}"""

    try:
        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=prompt,
        )
        return jsonify({"reply": response.text})
    except Exception as e:
        return jsonify({"error": f"API Error: {str(e)}"}), 500

if __name__ == "__main__":
    # Render assigns an automated network port using this environment check
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
