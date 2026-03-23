import os

OUTPUT_FILE = "CRE_SaaS_Architecture.md"

def generate_tree(dir_path, prefix=""):
    """Generate a tree string for a directory."""
    files = sorted(os.listdir(dir_path))
    # Exclude unwanted directories
    files = [f for f in files if f not in ("__pycache__", ".git", ".DS_Store")]
    
    tree_str = ""
    for i, file in enumerate(files):
        path = os.path.join(dir_path, file)
        is_last = i == len(files) - 1
        
        tree_str += prefix
        if is_last:
            tree_str += "└── "
            new_prefix = prefix + "    "
        else:
            tree_str += "├── "
            new_prefix = prefix + "│   "
            
        tree_str += file + "\n"
        
        if os.path.isdir(path):
            tree_str += generate_tree(path, new_prefix)
            
    return tree_str

def compile_docs():
    with open(OUTPUT_FILE, "w") as out:
        out.write("# Content Refactoring Engine (CRE SaaS MVP)\n\n")
        out.write("## 1. Multi-Model Architecture Overview\n\n")
        out.write("This engine implements an enterprise-grade Semantic Validation Pipeline:\n")
        out.write("`Retrieval (Google/DDG)` -> `Scraping (Trafilatura)` -> `Embedding (Local MiniLM)` -> `Similarity Math (Cosine)` -> `Reasoning (DeepSeek/Groq/OpenRouter)` -> `Rewrite (Gemini/Groq/OpenRouter)`\n\n")
        
        out.write("## 2. Evolution of the Architecture (V1 - V5)\n\n")
        out.write("The CRE SaaS platform has evolved through five major architectural iterations:\n\n")
        
        out.write("### V1: The Naive Full-HTML Rewrite\n")
        out.write("- **Methodology:** Sent raw HTML directly to GPT-4.\n")
        out.write("- **Fatal Flaw:** DOM structure corruption and tag hallucinations.\n\n")

        out.write("### V2: Regex Structure Locking\n")
        out.write("- **Methodology:** Protected tags with UUID placeholders.\n")
        out.write("- **Fatal Flaw:** Nested tag corruption and delimiter collisions.\n\n")

        out.write("### V3: Strict JSON Schema Batching (Enterprise Upgrade)\n")
        out.write("- **Methodology:** Converting DOM nodes to isolated JSON indices. Using `node.string` referencing.\n")
        out.write("- **Result:** 100% structural stability. Immunity to hallucinations.\n\n")

        out.write("### V4: The Multi-Tenant Control Layer\n")
        out.write("- **Methodology:** FastAPI backend with usage tracking, SQLite persistence, and local embedding fallbacks.\n\n")

        out.write("### V5: Triple-Redundancy & Dynamic UI (Phase 2 - Current)\n")
        out.write("- **Methodology:** Implemented a triple-tier LLM fallback chain (DeepSeek ➔ Groq ➔ OpenRouter) for 100% uptime. Added Server-Sent Events (SSE) for a Copyleaks-style real-time progress panel. Integrated persistent User History tracking.\n")
        out.write("- **The Result:** Professional, dynamic SaaS platform with no single point of failure and zero-latency user feedback loops.\n\n")

        out.write("## 3. Render Deployment\n\n")
        out.write("The application is configured for 1-click deployment on Render.com utilizing Infrastructure as Code (`render.yaml`).\n")
        out.write("1. Push the repository to GitHub.\n")
        out.write("2. Connect your Render account to the repository.\n")
        out.write("3. Dashboard ➔ Blueprint ➔ Connect `render.yaml`.\n")
        out.write("4. Render will automatically execute `./build.sh` to install dependencies and `./start.sh` to spin up the 4 Gunicorn production workers.\n")
        out.write("5. Add your API keys (`GEMINI_API_KEY`, `DEEPSEEK_API_KEY`, etc.) as Environment Variables in the Render dashboard.\n\n")

        out.write("## 4. Complete Folder Structure\n\n")
        out.write("```text\ncontent_refactor_engine/\n")
        
        # We only want to tree specific folders
        dirs_to_tree = ["backend", "frontend", "database"]
        
        for d in dirs_to_tree:
            if os.path.exists(d):
                out.write(f"├── {d}/\n")
                out.write(generate_tree(d, "│   "))
        out.write("```\n\n")
        
        out.write("### 📁 Module Descriptions\n\n")
        out.write("#### 🌐 Frontend (`frontend/`)\n")
        out.write("- **`index.html`**: The main user dashboard where they paste their article content.\n")
        out.write("- **`styles.css`**: All the styling for the application, including the \"shimmer/skeleton\" loading animations and the layout of the split-pane report view.\n")
        out.write("- **`app.js`**: The vanilla JavaScript logic that handles sending data to the backend, listening to the real-time Server-Sent Events (SSE) stream, and dynamically updating the UI progress bar.\n\n")
        
        out.write("#### 🗄️ Database (`database/`)\n")
        out.write("- **`cre.db`**: The single, portable SQLite3 database file that holds absolutely everything: user accounts, article histories (original vs rewritten content), and the local fingerprint plagiarism index.\n\n")

        out.write("#### ⚙️ Backend (`backend/`)\n")
        out.write("**1. Core Config & Entry Points**\n")
        out.write("- **`main.py`**: The entry point to the FastAPI application. It wires up CORS, the global exception handler, rate limiting, and attaches the routing files.\n")
        out.write("- **`.env`**: Stores all of your secret API keys (Gemini, OpenRouter, DeepSeek, Groq).\n")
        out.write("- **`config.py`**: Loads the `.env` variables into Python memory safely using Pydantic Settings.\n\n")

        out.write("**2. Models & Database (`backend/models/`)**\n")
        out.write("- **`database.py`**: Handles connecting to the `database/cre.db` SQLite file securely.\n")
        out.write("- **`article_model.py` / `report_model.py`**: Pydantic schemas (data shapes) that define exactly what data the frontend must send to the backend, and what data the backend will return.\n")
        out.write("- **`index_db.py`**: Houses the table structures for the new `indexed_documents` and `fingerprints` tables.\n\n")

        out.write("**3. API Routes (`backend/api/`)**\n")
        out.write("- **`controllers.py`**: The main traffic cop. It receives the HTTP request from the frontend and orchestrates the entire pipeline: Scraping -> Embedding -> Analysis -> Rewriting. It also streams the SSE updates back to the browser.\n")
        out.write("- **`auth_middleware.py`**: Checks if the user has an active API key or free trial limit remaining before letting them hit the expensive LLM endpoints.\n")
        out.write("- **`limits.py` & `usage_tracker.py`**: Enforces rate limiting (e.g., max 5 requests per day for free users) and tracks character counts in the SQLite database.\n\n")

        out.write("**4. The Pipeline Services (`backend/services/`)**\n")
        out.write("- **`query_generation.py`**: Uses DeepSeek/Groq to read the user's input article and figure out the 3 most important keyword search queries to test it against the internet.\n")
        out.write("- **`search_service.py`**: Takes those queries and searches them on Google Custom Search API or DuckDuckGo.\n")
        out.write("- **`scraper_service.py`**: Uses `Trafilatura` to visit the URLs found by the search service, bypass anti-bot protections, and extract the raw, readable text from those live competitor websites.\n")
        out.write("- **`embedding_service.py`**: Converts both the user's article and the scraped competitor articles into dense mathematical vectors (using a HuggingFace `sentence-transformers` model).\n")
        out.write("- **`similarity.py`**: Performs O(N x M) Cosine Similarity Math. It compares the vectors from the step above to generate a mathematical percentage.\n")
        out.write("- **`analysis_service.py`**: Hands the text over to your Heavy Reasoner LLMs (DeepSeek -> Groq -> OpenRouter) to grade it.\n")
        out.write("- **`rewrite_service.py`**: The final step. Hands the text to your Fast Writer LLMs (Gemini -> Groq -> OpenRouter) to completely refactor the sentence structures.\n")
        out.write("- **`fingerprint_engine.py`**: A fast algorithmic chunker that chops text into 5-word shingles and saves them in the database for instant offline plagiarism matching.\n\n")
        
        out.write("---\n\n## 5. Complete Source Code\n\n")
        
        # Traverse and dump code
        for root, dirs, files in os.walk("."):
            dirs[:] = [d for d in dirs if d not in ("__pycache__", ".git")]
            
            for file in sorted(files):
                # Only include relevant source files
                if file.endswith((".py", ".txt", ".html", ".js", ".css", ".sh", ".yaml")) and "venv" not in root and file != OUTPUT_FILE and not file.endswith(".md"):
                    file_path = os.path.join(root, file)
                    display_path = file_path.replace("./", "")
                    
                    lang = "text"
                    if file.endswith(".py"): lang = "python"
                    elif file.endswith(".html"): lang = "html"
                    elif file.endswith(".js"): lang = "javascript"
                    elif file.endswith(".css"): lang = "css"
                    
                    out.write(f"### `{display_path}`\n\n")
                    out.write(f"```{lang}\n")
                    
                    try:
                        with open(file_path, "r") as src:
                            out.write(src.read())
                    except Exception as e:
                        out.write(f"# Error reading file: {e}")
                        
                    out.write(f"\n```\n\n")

if __name__ == "__main__":
    compile_docs()
    print("Documentation generated successfully.")
