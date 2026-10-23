import os
import requests
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

GEMINI_API_KEY = "AQ.Ab8RN6K2VT8n2yjHxiEMemtyyOTBewTyspU4aACV74r3di-Lvg"
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
        textarea { width: 100%; padding: 12px; border-radius: 8px; border: 1px solid #d1d5db; box-sizing: border-box; }
        button { background: #2563eb; color: white; border: none; padding: 12px 24px; border-radius: 8px; cursor: pointer; width: 100%; margin-top: 5px; }
        .chat-box { background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 8px; padding: 15px; margin-top: 15px; min-height: 150px; }
    </style>
</head>
<body>
<div class="container">
    <div class="card">
        <h2>Interactive Query Prompt</h2>
        <textarea id="query" rows="3" placeholder="Type a query here..."></textarea>
        <button onclick="runQuery()">Execute RAG Search Pipeline</button>
        <div class="chat-box" id="chatContainer">Awaiting query...</div>
    </div>
</div>
<script>
async function runQuery() {
    const queryText = document.getElementById("query").value.trim();
    const chatContainer = document.getElementById("chatContainer");
    if (!queryText) return alert("Enter a question.");
    chatContainer.innerHTML = "Processing...";
    const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: queryText })
    });
    const data = await res.json();
    chatContainer.innerHTML = data.reply || data.error;
}
</script>
</body>
</html>"""

def read_local_documents():
    if not os.path.exists(DOCS_FOLDER):
        os.makedirs(DOCS_FOLDER)
    combined = ""
    for f in os.listdir(DOCS_FOLDER):
        if f.endswith(".txt"):
            with open(os.path.join(DOCS_FOLDER, f), "r", encoding="utf-8") as file:
                combined += file.read() + "\n"
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
    ctx = read_local_documents() or 'Default context: D-Drive password is "BlueSky-9942".'
    prompt = f"Context:\n{ctx}\n\nQuestion:\n{user_query}"
    try:
        res = requests.post(GEMINI_URL, headers=HEADERS, json={"contents": [{"parts": [{"text": prompt}]}]})
        return jsonify({"reply": res.json()["candidates"][0]["content"]["parts"][0]["text"]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
