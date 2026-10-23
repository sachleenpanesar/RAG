import os
from google import genai

# =====================================================================
#  STABLE RUNNER CONFIGURATION
# =====================================================================
GEMINI_API_KEY = "AQ.Ab8RN6JZ3xPjvjGMLphRoESsJfzt_I8T5BU1c4CfszlAiyA50w"
DOCS_FOLDER = r"D:\RAG Code\source_docs"

# Initialize the official Google GenAI Client
client = genai.Client(api_key=GEMINI_API_KEY)

# =====================================================================
#  NATIVE CONTEXT EXTRACTOR (ZERO DEPENDENCY LAYER)
# =====================================================================
def read_local_documents():
    """Reads all raw text files inside the source folder automatically."""
    if not os.path.exists(DOCS_FOLDER):
        os.makedirs(DOCS_FOLDER)
        print(f"Created folder at {DOCS_FOLDER}. Drop your .txt files there!")
        return ""

    combined_text = ""
    files = [f for f in os.listdir(DOCS_FOLDER) if f.endswith(".txt")]

    for filename in files:
        file_path = os.path.join(DOCS_FOLDER, filename)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                combined_text += f"\n--- DOCUMENT SOURCE: {filename} ---\n"
                combined_text += f.read() + "\n"
        except Exception as e:
            print(f" Warning: Could not read {filename}. Error: {e}")

    return combined_text.strip()

def ask_gemini_direct_rag(user_query):
    """Feeds text files directly into the context window to answer queries."""
    # 1. Gather all knowledge text data dynamically from disk
    all_context = read_local_documents()
    
    if not all_context:
        all_context = "No documents found in source_docs folder. The folder is currently empty."

    # 2. Build a localized reference prompt
    prompt = f"""You are a helpful AI assistant. Answer the user's question using ONLY the provided context blocks extracted from local documentation.
If the answer cannot be found in the context text, state clearly that you do not have that information.

LOCAL FILE DATA:
{all_context}

USER QUESTION:
{user_query}"""

    # 3. Generate content using the stable generation model
    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=prompt,
    )
    return response.text

# =====================================================================
# LIVE RUNNER LOOP
# =====================================================================
if __name__ == "__main__":
    print("--- STARTING AUTOMATED LIVE-CONTEXT RAG PIPELINE ---")
    
    # Verify folder path state
    if not os.path.exists(DOCS_FOLDER):
        os.makedirs(DOCS_FOLDER)
        print(f"Initialized blank source folder directory at: {DOCS_FOLDER}")
        
    print("\n System ready! Ask a question about your documents (or type 'exit' to quit):")
    
    while True:
        user_input = input("\nYou: ").strip()
        if user_input.lower() == 'exit':
            print("Goodbye!")
            break
        if not user_input:
            continue
            
        try:
            print(" Scanning raw text documents on disk...")
            answer = ask_gemini_direct_rag(user_input)
            print(f"\nBot: {answer}")
        except Exception as e:
            print(f"\n Operational Error: {e}")
