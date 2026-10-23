
import os
import requests
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# =====================================================================
# 🛠️ CZYSTA KONFIGURACJA KLUCZA I ADRESU URL (Klucz oddzielony od domeny)
# =====================================================================
GEMINI_API_KEY = "AQ.Ab8RN6K2VT8n2yjHxiEMemtyyOTBewTyspU4aACV74r3di-Lvg"

# Zwróć uwagę na znak zapytania oraz przypisanie zmiennej 'key=' na końcu adresu:
GEMINI_URL = f"https://googleapis.com{GEMINI_API_KEY}"
HEADERS = {"Content-Type": "application/json"}
# =====================================================================


DOCS_FOLDER = "source_docs"

# =====================================================================
# 🎨 NATIVE HTML VISUAL PAGE LAYOUT
# =====================================================================
HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Retrieval-Augmented Generation Dashboard</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 0; background-color: #f3f4f6; color: #1f2937; }
        .navbar { background-color: #1e3a8a; color: white; padding: 15px 20px; font-weight: bold; font-size: 1.2rem; display: flex; align-items: center; justify-content: space-between; }
        .badge { background-color: #10b981; color: white; padding: 4px 8px; border-radius: 12px; font-size: 0.8rem; }
        .container { max-width: 900px; margin: 40px auto; padding: 0 20px; }
        .card { background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 25px; }
        h2 { margin-top: 0; color: #1e3a8a; font-size: 1.4rem; border-bottom: 2px solid #e5e7eb; padding-bottom: 8px; }
        p { line-height: 1.6; color: #4b5563; }
        .input-group { margin-bottom: 20px; }
        label { display: block; font-weight: 600; margin-bottom: 8px; color: #374151; }
        textarea { width: 100%; padding: 12px; border: 1px solid #d1d5db; border-radius: 8px; box-sizing: border-box; font-size: 1rem; background-color: #f9fafb; resize: vertical; }
        textarea:focus { outline: none; border-color: #2563eb; background-color: white; }
        .chip-container { display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 15px; }
        .chip { background-color: #eff6ff; color: #2563eb; border: 1px solid #bfdbfe; padding: 8px 14px; border-radius: 20px; font-size: 0.9rem; font-weight: 500; cursor: pointer; transition: all 0.2s; user-select: none; }
        .chip:hover { background-color: #dbeafe; color: #1d4ed8; border-color: #93c5fd; }
        button { background-color: #2563eb; color: white; border: none; padding: 12px 24px; font-size: 1rem; font-weight: 600; border-radius: 8px; cursor: pointer; transition: background 0.2s; width: 100%; margin-top: 5px; }
        button:hover { background-color: #1d4ed8; }
        .chat-box { background-color: #f9fafb; border: 1px solid #e5e7eb; border-radius: 8px; min-height: 150px; max-height: 300px; overflow-y: auto; padding: 15px; margin-top: 15px; }
        .message { margin-bottom: 15px; padding: 10px 14px; border-radius: 8px; max-width: 85%; line-height: 1.5; font-size: 1rem; }
        .user-msg { background-color: #dbeafe; color: #1e40af; margin-left: auto; text-align: right; }
        .bot-msg { background-color: #e5e7eb; color: #1f2937; white-space: pre-wrap; }
        .doc-box { background-color: #fef3c7; border-left: 4px solid #d97706; padding: 15px; border-radius: 4px; font-family: monospace; font-size: 0.9rem; white-space: pre-wrap; }
    </style>
</head>
<body>

<div class="navbar">
    <span>🤖 Automated Cloud RAG Pipeline</span>
    <span class="badge">100% Hosted on Render</span>
</div>

<div class="container">
    <div class="card">
        <h2>🗂️ Stored Context Documentation (Active Knowledge Base)</h2>
        <p>This text block mimics the local .txt files read dynamically from disk during localized runtime operations:</p>
        <div class="doc-box">The master control password for the D-Drive automated server cluster is "BlueSky-9942". 
This password was changed on October 23, 2026, by the chief systems manager.
Do not share this information with unverified engineers.</div>
    </div>

    <div class="card">
        <h2>💬 Interactive Query Prompt</h2>
        <p style="margin-bottom: 20px; font-size: 0.95rem; color: #6b7280;">Click a suggestion below to test the context injection automatically, or type your own question:</p>
        
        <div class="chip-container">
            <div class="chip" onclick="fillPrompt('What is the server cluster password?')">🔑 Ask for Password</div>
            <div class="chip" onclick="fillPrompt('When was the password changed and by whom?')">📅 Ask for Date & Manager</div>
            <div class="chip" onclick="fillPrompt('What is the guest lounge Wi-Fi password?')">🛡️ Test Hallucination Rejection</div>
        </div>

        <div class="input-group">
            <textarea id="query" rows="3" placeholder="Click an example above or type a query here..."></textarea>
        </div>
        <button onclick="runQuery()">Execute RAG Search Pipeline</button>
        
        <div class="chat-box" id="chatContainer">
            <p style="color: #9ca3af; text-align: center; margin-top: 50px;">Awaiting pipeline execution query input...</p>
        </div>
    </div>
</div>

<script>
function fillPrompt(text) {
    document.getElementById("query").value = text;
}

async function runQuery() {
    const queryText = document.getElementById("query").value.trim();
    const chatContainer = document.getElementById("chatContainer");

    if (!queryText) {
        alert("Please select or enter a question first.");
        return;
    }

    chatContainer.innerHTML = `<div class="message user-msg">${queryText}</div><div class="message bot-msg">🔍 Processing query on server...</div>`;

    try {
        const response = await fetch("/api/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query: queryText })
        });

        const data = await response.json();
        
        if (data.reply) {
            chatContainer.innerHTML = `
                <div class="message user-msg">${queryText}</div>
                <div class="message bot-msg">${data.reply}</div>
            `;
        } else {
            throw new Error(data.error || "Server processing failure");
        }
    } catch (error) {
        console.error(error);
        chatContainer.innerHTML = `
            <div class="message user-msg">${queryText}</div>
            <div class="message bot-msg" style="color: #dc2626; background-color: #fef2f2; border: 1px solid #fca5a5;">
                ❌ Server Error: ${error.message || "Failed to communicate with pipeline engine."}
            </div>
        `;
    }
}
</script>

</body>
</html>
"""

def read_local_documents():
    if not os.path.exists(DOCS_FOLDER):
        os.makedirs(DOCS_FOLDER)
        return ""
    combined_text = ""
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
    return render_template_string(HTML_PAGE)

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json or {}
    user_query = data.get("query", "").strip()

    if not user_query:
        return jsonify({"error": "Query text is required"}), 400

    all_context = read_local_documents()
    if not all_context:
        all_context = 'The master control password for the D-Drive automated server cluster is "BlueSky-9942". This password was changed on October 23, 2026, by the chief systems manager. Do not share this information with unverified engineers.'

    prompt = f"Answer the user's question using ONLY the provided context blocks.\n\nCONTEXT:\n{all_context}\n\nQUESTION:\n{user_query}"

    # ✅ BYPASSES THE CLIENT SDK: Uses raw HTTP requests which cleanly support your exact AQ. key token
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    
    try:
        response = requests.post(GEMINI_URL, headers=HEADERS, json=payload)
        res_json = response.json()
        
        if response.status_code != 200:
            return jsonify({"error": f"Google API Error {response.status_code}: {response.text}"}), 500
            
        bot_reply = res_json["candidates"][0]["content"]["parts"][0]["text"]
        return jsonify({"reply": bot_reply})
    except Exception as e:
        return jsonify({"error": f"Server Parsing Error: {str(e)}"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
