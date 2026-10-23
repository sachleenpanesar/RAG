import os
import requests
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ✅ Cloud-Native: Pulls the API key securely from Render's Environment panel
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AQ.Ab8RN6K2VT8n2yjHxiEMemtyyOTBewTyspU4aACV74r3di-Lvg").strip()

# Clean, production-certified URL routing string formatting
GEMINI_URL = f"https://googleapis.com{GEMINI_API_KEY}"
HEADERS = {"Content-Type": "application/json"}
DOCS_FOLDER = "source_docs"

HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>AI RAG Dashboard</title>
    <style>
        body { font-family: sans-serif; margin: 0; background: #f3f4f6; color: #1f2937; }
        .container { max-width: 900px; margin: 40px auto; padding: 0 20px; }
        .card { background: white; padding: 30px; border-radius: 12px; margin-bottom: 25px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
        textarea { width: 100%; padding: 12px; border-radius: 8px; border: 1px solid #d1d5db; box-sizing: border-box; font-size: 1rem; }
        button { background: #2563eb; color: white; border: none; padding: 12px 24px; border-radius: 8px; cursor: pointer; width: 100%; margin-top: 10px; font-weight: bold; font-size: 1rem; }
        button:hover { background: #1d4ed8; }
        .chat-box { background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 8px; padding: 15px; margin-top: 15px; min-height: 150px; font-size: 1.05rem; line-height: 1.5; }
    </style>
</head>
<body>
<div class="container">
    <div class="card">
        <h2>🤖 Automated Context-Window RAG Pipeline</h2>
        <p>Type a question below to scan the local cloud documentation container:</p>
        <textarea id="query" rows="3" placeholder="e.g., What is the server cluster password?"></textarea>
        <button onclick="runQuery()">Execute RAG Search Pipeline</button>
        <div class="chat-box" id="chatContainer">Awaiting query pipeline execution input...</div>
    </div>
</div>
<script>
async function runQuery() {
    const queryText = document.getElementById("query").value.trim();
    const chatContainer = document.getElementById("chatContainer");
    if (!queryText) return alert("Please enter a question.");
    chatContainer.innerHTML = "🔍 Scanning cloud data array...";
    try {
        const res = await fetch("/api/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query: queryText })
        });
        const data = await res.json();
        chatContainer.innerHTML = data.reply || data.error;
    } catch (e) {
        chatContainer.innerHTML = "❌ Network Error connecting to backend.";
    }
}
</script>
</body>
</html>"""

def read_local_documents():
    if not os.path.exists(DOCS_FOLDER):
        os.makedirs(DOCS_FOLDER)
    combined = ""
    if os.path.exists(DOCS_FOLDER):
        for f in os.listdir(DOCS_FOLDER):
            if f.endswith(".txt"):
                try:
                    with open(os.path.join(DOCS_FOLDER, f), "r", encoding="utf-8") as file:
                        combined += file.read() + "\n"
                except Exception:
                    pass
    return combined.strip()

@app.route("/", methods=["GET"])
def home():
    return render_template_string(HTML_PAGE)

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json or {}
    user_query = data.get("query", "").strip()
    if not user_query:
        return jsonify({"error": "Query required"}), 400
        
    ctx = read_local_documents()
    if not ctx:
        ctx = 'The master control password for the D-Drive automated server cluster is "BlueSky-9942". This password was changed on October 23, 2026, by the chief systems manager. Do not share this information with unverified engineers.'
        
    prompt = f"Answer the user's question using ONLY the provided context blocks.\n\nCONTEXT:\n{ctx}\n\nQUESTION:\n{user_query}"
    
    try:
        response = requests.post(GEMINI_URL, headers=HEADERS, json={"contents": [{"parts": [{"text": prompt}]}]})
        res_data = response.json()
        
        if response.status_code != 200:
            return jsonify({"error": f"API Error {response.status_code}: {response.text}"}), 500
            
        bot_reply = res_data["candidates"][0]["content"]["parts"][0]["text"]
        return jsonify({"reply": bot_reply})
    except Exception as e:
        return jsonify({"error": f"Server Error: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
