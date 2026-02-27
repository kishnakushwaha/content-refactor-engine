# Content Refactoring Engine (CRE SaaS MVP)

## 1. Multi-Model Architecture Overview

This engine implements an enterprise-grade Semantic Validation Pipeline:
`Retrieval (Google/DDG)` -> `Scraping (Trafilatura)` -> `Embedding (Local MiniLM)` -> `Similarity Math (Cosine)` -> `Reasoning (DeepSeek/Groq/OpenRouter)` -> `Rewrite (Gemini/Groq/OpenRouter)`

## 2. Evolution of the Architecture (V1 - V5)

The CRE SaaS platform has evolved through five major architectural iterations:

### V1: The Naive Full-HTML Rewrite
- **Methodology:** Sent raw HTML directly to GPT-4.
- **Fatal Flaw:** DOM structure corruption and tag hallucinations.

### V2: Regex Structure Locking
- **Methodology:** Protected tags with UUID placeholders.
- **Fatal Flaw:** Nested tag corruption and delimiter collisions.

### V3: Strict JSON Schema Batching (Enterprise Upgrade)
- **Methodology:** Converting DOM nodes to isolated JSON indices. Using `node.string` referencing.
- **Result:** 100% structural stability. Immunity to hallucinations.

### V4: The Multi-Tenant Control Layer
- **Methodology:** FastAPI backend with usage tracking, SQLite persistence, and local embedding fallbacks.

### V5: Triple-Redundancy & Dynamic UI (Phase 2 - Current)
- **Methodology:** Implemented a triple-tier LLM fallback chain (DeepSeek ➔ Groq ➔ OpenRouter) for 100% uptime. Added Server-Sent Events (SSE) for a Copyleaks-style real-time progress panel. Integrated persistent User History tracking.
- **The Result:** Professional, dynamic SaaS platform with no single point of failure and zero-latency user feedback loops.

## 3. Render Deployment

The application is configured for 1-click deployment on Render.com utilizing Infrastructure as Code (`render.yaml`).
1. Push the repository to GitHub.
2. Connect your Render account to the repository.
3. Dashboard ➔ Blueprint ➔ Connect `render.yaml`.
4. Render will automatically execute `./build.sh` to install dependencies and `./start.sh` to spin up the 4 Gunicorn production workers.
5. Add your API keys (`GEMINI_API_KEY`, `DEEPSEEK_API_KEY`, etc.) as Environment Variables in the Render dashboard.

## 4. Complete Folder Structure

```text
content_refactor_engine/
├── backend/
│   ├── .env
│   ├── api
│   │   ├── auth_middleware.py
│   │   ├── controllers.py
│   │   └── routes.py
│   ├── config.py
│   ├── main.py
│   ├── models
│   │   ├── article_model.py
│   │   ├── database.py
│   │   └── report_model.py
│   ├── requirements.txt
│   ├── services
│   │   ├── analysis_service.py
│   │   ├── embedding_service.py
│   │   ├── limit_service.py
│   │   ├── query_generator.py
│   │   ├── retrieval_engine.py
│   │   ├── rewrite_service.py
│   │   ├── scoring_service.py
│   │   ├── scraper_service.py
│   │   ├── search_service.py
│   │   ├── similarity_service.py
│   │   └── usage_service.py
│   └── utils
│       ├── helpers.py
│       ├── logger.py
│       ├── text_cleaner.py
│       └── url_validator.py
├── frontend/
│   ├── app.js
│   ├── index.html
│   └── styles.css
├── database/
│   └── cre.db
```

---

## 5. Complete Source Code

### `build.sh`

```text
#!/usr/bin/env bash
# build.sh

# Exit on error
set -o errexit

echo "Installing backend dependencies..."
cd backend
pip install --upgrade pip
pip install -r requirements.txt

# Create database directory if it doesn't exist
cd ..
mkdir -p database
echo "Build complete."

```

### `generate_docs.py`

```python
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

```

### `render.yaml`

```text
services:
  - type: web
    name: cre-saas
    # Use python environment
    runtime: python
    # We define the build and start commands explicitly
    buildCommand: "./build.sh"
    startCommand: "./start.sh"
    # Choose region
    region: ohio
    # Free tier or starter
    plan: free
    # Environment variables required for the app to function
    envVars:
      - key: GEMINI_API_KEY
        sync: false
      - key: DEEPSEEK_API_KEY
        sync: false
      - key: GROQ_API_KEY
        sync: false
      - key: OPENROUTER_API_KEY
        sync: false
      - key: HUGGINGFACE_API_KEY
        sync: false
      - key: GOOGLE_CX_ID
        sync: false
      - key: GOOGLE_API_KEY
        sync: false
      - key: FREE_PLAN_MAX_WORDS
        value: 3000
      - key: FREE_PLAN_MAX_REQUESTS_PER_DAY
        value: 10
      - key: PYTHON_VERSION
        value: 3.10.12
    # Optional: If you upgrade to a paid Render plan, you can attach a persistent disk for the SQLite DB to survive redeploys.
    # disk:
    #   name: cre-data
    #   mountPath: /opt/render/project/src/database
    #   sizeGB: 1

```

### `requirements.txt`

```text
fastapi
uvicorn
python-dotenv
beautifulsoup4
lxml
openai
groq
pydantic

```

### `start.sh`

```text
#!/usr/bin/env bash
# start.sh

# Exit on error
set -o errexit

echo "Starting FastAPI Production Server..."
cd backend

# Use Gunicorn as a process manager with Uvicorn workers for production stability
# Uses the PORT environment variable provided automatically by Render
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT

```

### `frontend/app.js`

```javascript
document.addEventListener('DOMContentLoaded', () => {
    const processBtn = document.getElementById('process-btn');
    const articleInput = document.getElementById('article-input');
    const wordCount = document.getElementById('input-word-count');
    const apiKeyInput = document.getElementById('api-key-input');
    const tabs = document.querySelectorAll('.tab');

    // UI Elements
    const emptyState = document.getElementById('empty-state');
    const progressPanel = document.getElementById('progress-panel');
    const reportResults = document.getElementById('report-results');
    const outputHtml = document.getElementById('output-html');
    const btnText = document.querySelector('.btn-text');
    const loader = document.querySelector('.loader');

    // Progress Elements
    const progressSteps = document.getElementById('progress-steps');
    const progressBarFill = document.getElementById('progress-bar-fill');
    const progressPercent = document.getElementById('progress-percent');

    // Step configuration matching backend progress_callback steps
    const STEP_CONFIG = {
        extracting: { label: 'Breaking down your text for in-depth analysis...', icon: '📝', percent: 10 },
        searching: { label: 'Analyzing billions of web pages for matching content...', icon: '🔍', percent: 30 },
        comparing: { label: 'Scanning millions of publications for potential matches...', icon: '📊', percent: 50 },
        analyzing: { label: 'Ensuring your content is uniquely yours...', icon: '🧠', percent: 70 },
        rewriting: { label: 'Analyzing for advanced rewording and paraphrasing...', icon: '✍️', percent: 85 },
        finalizing: { label: 'Generating your comprehensive report...', icon: '📋', percent: 95 },
        complete: { label: 'Analysis complete!', icon: '✅', percent: 100 }
    };

    // Live word count
    articleInput.addEventListener('input', () => {
        const words = articleInput.value.trim().split(/\s+/).filter(w => w.length > 0).length;
        wordCount.textContent = `${words} words`;
    });

    // Tab switching
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

            tab.classList.add('active');
            document.getElementById(`tab-${tab.dataset.tab}`).classList.add('active');

            // Load history when History tab is clicked
            if (tab.dataset.tab === 'history') {
                loadHistory();
            }
        });
    });

    // =============================
    // SSE STREAMING PROCESS
    // =============================
    processBtn.addEventListener('click', async () => {
        const content = articleInput.value.trim();
        const apiKey = apiKeyInput.value.trim();

        if (!content) {
            showToast('Please paste an article first.', 'error');
            return;
        }

        if (!apiKey) {
            showToast('API Key is required.', 'error');
            return;
        }

        // Set Loading State
        processBtn.disabled = true;
        btnText.textContent = 'Processing...';
        loader.classList.remove('hidden');

        // Show progress panel
        emptyState.classList.add('hidden');
        reportResults.classList.add('hidden');
        progressPanel.classList.remove('hidden');
        progressSteps.innerHTML = '';
        progressBarFill.style.width = '0%';
        progressPercent.textContent = 'Loading... 0%';

        // Switch to Analysis tab
        tabs.forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
        tabs[0].classList.add('active');
        document.getElementById('tab-report').classList.add('active');

        let completedSteps = [];

        try {
            const response = await fetch('/api/process-stream', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-API-Key': apiKey
                },
                body: JSON.stringify({ content })
            });

            if (!response.ok) {
                let errMsg = 'Processing failed';
                try {
                    const errData = await response.json();
                    errMsg = errData.detail || errData.message || errMsg;
                } catch (e) {
                    errMsg = await response.text() || errMsg;
                }
                throw new Error(errMsg);
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split('\n');
                buffer = lines.pop();

                for (const line of lines) {
                    if (!line.startsWith('data: ')) continue;
                    const jsonStr = line.slice(6).trim();
                    if (!jsonStr) continue;

                    try {
                        const event = JSON.parse(jsonStr);

                        if (event.step === 'complete') {
                            // Mark all steps as done
                            document.querySelectorAll('.progress-step').forEach(s => {
                                s.classList.remove('active');
                                s.classList.add('done');
                                const icon = s.querySelector('.step-icon');
                                icon.classList.remove('active');
                                icon.classList.add('done');
                                icon.innerHTML = '<span class="check">✓</span>';
                            });
                            progressBarFill.style.width = '100%';
                            progressPercent.textContent = 'Loading... 100%';

                            // Short delay then show results
                            await new Promise(r => setTimeout(r, 800));
                            progressPanel.classList.add('hidden');
                            renderReport(event.result);
                            showToast('Refactoring complete!');
                        } else {
                            // Mark previous steps as done
                            document.querySelectorAll('.progress-step.active').forEach(s => {
                                s.classList.remove('active');
                                s.classList.add('done');
                                const icon = s.querySelector('.step-icon');
                                icon.classList.remove('active');
                                icon.classList.add('done');
                                icon.innerHTML = '<span class="check">✓</span>';
                            });

                            // Add new active step
                            const config = STEP_CONFIG[event.step] || { label: event.message, icon: '⚡', percent: 50 };
                            addProgressStep(config.icon, event.message || config.label, true);
                            progressBarFill.style.width = config.percent + '%';
                            progressPercent.textContent = `Loading... ${config.percent}%`;
                        }
                    } catch (e) {
                        // Skip malformed events
                    }
                }
            }

        } catch (error) {
            progressPanel.classList.add('hidden');
            emptyState.classList.remove('hidden');
            showToast(error.message, 'error');
        } finally {
            processBtn.disabled = false;
            btnText.textContent = 'Analyze & Refactor';
            loader.classList.add('hidden');
        }
    });

    function addProgressStep(icon, text, isActive) {
        const step = document.createElement('div');
        step.className = `progress-step ${isActive ? 'active' : ''}`;
        step.innerHTML = `
            <div class="step-icon ${isActive ? 'active' : 'done'}">
                ${isActive ? '<div class="spinner"></div>' : '<span class="check">✓</span>'}
            </div>
            <span class="step-text">${text}</span>
        `;
        progressSteps.appendChild(step);

        // Auto-scroll to latest step
        step.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    // =============================
    // RENDER REPORT
    // =============================
    function renderReport(data) {
        reportResults.classList.remove('hidden');

        const report = data.report || {};

        const isPlagiarismDetected = report.similarity_score !== "No significant matches found.";
        const simScoreNum = isPlagiarismDetected ? parseInt(report.similarity_score) : 0;

        // Update Meters
        document.getElementById('sim-score').textContent = isPlagiarismDetected ? report.similarity_score : "0%";
        document.getElementById('sim-fill').style.width = isPlagiarismDetected ? report.similarity_score : "0%";

        // Color coding similarity
        const simFill = document.getElementById('sim-fill');
        if (simScoreNum > 80) simFill.style.backgroundColor = 'var(--danger)';
        else if (simScoreNum > 40) simFill.style.backgroundColor = 'var(--warning)';
        else simFill.style.backgroundColor = 'var(--success)';

        document.getElementById('orig-score').textContent = report.originality_score || "--%";
        document.getElementById('orig-fill').style.width = report.originality_score || "0%";

        const trust = report.trust_score || "0/10";
        document.getElementById('trust-score').textContent = trust.split('/')[0];
        document.getElementById('trust-fill').style.width = `${(parseInt(trust) / 10) * 100}%`;

        // Qualitative Badges
        const riskBadge = document.getElementById('risk-badge');
        const safety = report.adsense_safety || "--";
        riskBadge.textContent = safety;
        riskBadge.className = 'badge';
        if (safety.toLowerCase().includes('high')) riskBadge.classList.add('risk');
        else if (safety.toLowerCase().includes('medium')) riskBadge.classList.add('warn');
        else riskBadge.classList.add('safe');

        document.getElementById('idea-badge').textContent = report.idea_similarity || "--";

        // URL
        const topRef = document.getElementById('top-ref-link');
        const topUrl = report.top_match_url;

        if (topUrl) {
            topRef.textContent = topUrl;
            topRef.href = topUrl;
        } else {
            topRef.textContent = "None detected";
            topRef.removeAttribute('href');
        }

        // Output HTML
        outputHtml.innerHTML = data.final_html || "<i>No content returned.</i>";
    }

    // =============================
    // HISTORY
    // =============================
    async function loadHistory() {
        const apiKey = apiKeyInput.value.trim();
        if (!apiKey) return;

        const historyEmpty = document.getElementById('history-empty');
        const historyList = document.getElementById('history-list');

        try {
            const response = await fetch('/api/history', {
                headers: { 'X-API-Key': apiKey }
            });

            if (!response.ok) return;

            const data = await response.json();
            const history = data.history || [];

            if (history.length === 0) {
                historyEmpty.classList.remove('hidden');
                historyList.classList.add('hidden');
                return;
            }

            historyEmpty.classList.add('hidden');
            historyList.classList.remove('hidden');
            historyList.innerHTML = '';

            for (const item of history) {
                const simStr = item.semantic_similarity_score || '0%';
                const sim = parseInt(simStr) || 0;
                const scoreClass = sim > 70 ? 'high' : sim > 30 ? 'mid' : 'low';
                const date = item.created_at ? new Date(item.created_at).toLocaleString() : 'Unknown';
                const preview = (item.original_content || '').substring(0, 120) + '...';

                const el = document.createElement('div');
                el.className = 'history-item';
                el.innerHTML = `
                    <div class="history-meta">
                        <span class="history-date">${date}</span>
                        <span class="history-score ${scoreClass}">${sim}% similar</span>
                    </div>
                    <p class="history-preview">${preview}</p>
                `;
                historyList.appendChild(el);
            }

        } catch (err) {
            console.error('History load failed:', err);
        }
    }

    // =============================
    // TOASTS
    // =============================
    function showToast(message, type = 'success') {
        const container = document.getElementById('toast-container');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;

        container.appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = '0';
            setTimeout(() => toast.remove(), 300);
        }, 4000);
    }
});

```

### `frontend/index.html`

```html
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CRE | Content Refactoring Engine</title>
    <meta name="description" content="AI-powered plagiarism detection and content refactoring SaaS platform">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="/styles.css">
</head>

<body>
    <div class="glow-bg"></div>
    <div class="glow-bg secondary"></div>

    <main class="container">
        <header>
            <div class="logo-container">
                <div class="logo-icon"></div>
                <h1>CRE<span>SaaS</span></h1>
            </div>
            <div class="api-key-container">
                <input type="password" id="api-key-input" placeholder="Enter X-API-Key" value="cre-admin-key-12345">
                <div class="status-dot"></div>
            </div>
        </header>

        <section class="workspace">
            <div class="panel input-panel">
                <div class="panel-header">
                    <h2>Input Article</h2>
                    <span class="word-count" id="input-word-count">0 words</span>
                </div>
                <textarea id="article-input"
                    placeholder="Paste your article here to sanitize, rewrite, and make AdSense-safe..."></textarea>
                <button id="process-btn" class="primary-btn">
                    <span class="btn-text">Analyze & Refactor</span>
                    <div class="loader hidden"></div>
                </button>
            </div>

            <div class="panel output-panel">
                <div class="panel-header">
                    <h2>CRE Report & Output</h2>
                    <div class="tabs">
                        <button class="tab active" data-tab="report">Analysis</button>
                        <button class="tab" data-tab="content">Refactored Content</button>
                        <button class="tab" data-tab="history">History</button>
                    </div>
                </div>

                <div class="tab-content active" id="tab-report">
                    <!-- Empty State -->
                    <div class="empty-state" id="empty-state">
                        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                            stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                            <polyline points="14 2 14 8 20 8"></polyline>
                            <line x1="16" y1="13" x2="8" y2="13"></line>
                            <line x1="16" y1="17" x2="8" y2="17"></line>
                            <polyline points="10 9 9 9 8 9"></polyline>
                        </svg>
                        <p>Awaiting article processing...</p>
                    </div>

                    <!-- Live Progress Panel (Copyleaks-style) -->
                    <div class="progress-panel hidden" id="progress-panel">
                        <div class="progress-header">
                            <div class="progress-bar-container">
                                <div class="progress-bar-fill" id="progress-bar-fill"></div>
                            </div>
                            <span class="progress-percent" id="progress-percent">Loading... 0%</span>
                        </div>
                        <div class="progress-steps" id="progress-steps">
                            <!-- Steps will be injected dynamically -->
                        </div>
                        <div class="skeleton-results">
                            <div class="skeleton-block"></div>
                            <div class="skeleton-block short"></div>
                            <div class="skeleton-block"></div>
                            <div class="skeleton-block shorter"></div>
                            <div class="skeleton-block"></div>
                        </div>
                    </div>

                    <!-- Results -->
                    <div class="report-container hidden" id="report-results">
                        <div class="score-cards">
                            <div class="score-card">
                                <h3>Similarity</h3>
                                <div class="score-value" id="sim-score">--%</div>
                                <div class="score-bar">
                                    <div class="fill" id="sim-fill"></div>
                                </div>
                            </div>
                            <div class="score-card">
                                <h3>Originality</h3>
                                <div class="score-value" id="orig-score">--%</div>
                                <div class="score-bar">
                                    <div class="fill" id="orig-fill"></div>
                                </div>
                            </div>
                            <div class="score-card">
                                <h3>Trust Score</h3>
                                <div class="score-value" id="trust-score">--/10</div>
                                <div class="score-bar">
                                    <div class="fill" id="trust-fill"></div>
                                </div>
                            </div>
                        </div>

                        <div class="analysis-details">
                            <div class="detail-row">
                                <span class="label">AdSense Risk:</span>
                                <span class="badge" id="risk-badge">--</span>
                            </div>
                            <div class="detail-row">
                                <span class="label">Idea Similarity:</span>
                                <span class="badge outline" id="idea-badge">--</span>
                            </div>
                            <div class="detail-row">
                                <span class="label">Top Reference:</span>
                                <a href="#" target="_blank" id="top-ref-link" class="truncate-link">None detected</a>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="tab-content" id="tab-content">
                    <div class="rewritten-html-container">
                        <div id="output-html" class="output-content"></div>
                    </div>
                </div>

                <div class="tab-content" id="tab-history">
                    <div class="history-container" id="history-container">
                        <div class="empty-state" id="history-empty">
                            <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                                stroke-width="1.5">
                                <circle cx="12" cy="12" r="10"></circle>
                                <polyline points="12 6 12 12 16 14"></polyline>
                            </svg>
                            <p>No scan history yet</p>
                        </div>
                        <div class="history-list hidden" id="history-list"></div>
                    </div>
                </div>
            </div>
        </section>

        <div id="toast-container"></div>
    </main>

    <script src="/app.js"></script>
</body>

</html>
```

### `frontend/styles.css`

```css
:root {
    --bg-dark: #0f172a;
    --panel-bg: rgba(30, 41, 59, 0.7);
    --border-color: rgba(255, 255, 255, 0.1);
    --text-primary: #f8fafc;
    --text-secondary: #94a3b8;
    --accent: #3b82f6;
    --accent-hover: #2563eb;
    --success: #10b981;
    --warning: #f59e0b;
    --danger: #ef4444;
}

* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

body {
    background-color: var(--bg-dark);
    color: var(--text-primary);
    font-family: 'Inter', sans-serif;
    min-height: 100vh;
    overflow-x: hidden;
    position: relative;
}

.glow-bg {
    position: absolute;
    width: 600px;
    height: 600px;
    background: radial-gradient(circle, rgba(59, 130, 246, 0.15) 0%, rgba(15, 23, 42, 0) 70%);
    top: -200px;
    left: -200px;
    z-index: -1;
    filter: blur(40px);
}

.glow-bg.secondary {
    background: radial-gradient(circle, rgba(139, 92, 246, 0.1) 0%, rgba(15, 23, 42, 0) 70%);
    bottom: -200px;
    right: -100px;
    top: auto;
    left: auto;
}

.container {
    max-width: 1400px;
    margin: 0 auto;
    padding: 2rem;
    display: flex;
    flex-direction: column;
    height: 100vh;
}

header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
}

.logo-container {
    display: flex;
    align-items: center;
    gap: 1rem;
}

.logo-icon {
    width: 32px;
    height: 32px;
    background: linear-gradient(135deg, var(--accent), #8b5cf6);
    border-radius: 8px;
}

h1 {
    font-size: 1.5rem;
    font-weight: 700;
    letter-spacing: -0.5px;
}

h1 span {
    color: var(--accent);
    font-weight: 400;
}

.api-key-container {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    background: rgba(0, 0, 0, 0.2);
    padding: 0.5rem 1rem;
    border-radius: 99px;
    border: 1px solid var(--border-color);
}

.api-key-container input {
    background: transparent;
    border: none;
    color: var(--text-secondary);
    font-family: monospace;
    outline: none;
    width: 250px;
}

.status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background-color: var(--success);
    box-shadow: 0 0 10px var(--success);
}

.workspace {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 2rem;
    flex-grow: 1;
    min-height: 0;
}

.panel {
    background: var(--panel-bg);
    backdrop-filter: blur(12px);
    border: 1px solid var(--border-color);
    border-radius: 16px;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
}

.panel-header {
    min-height: 64px;
    padding: 0 1.5rem;
    border-bottom: 1px solid var(--border-color);
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.panel-header h2 {
    font-size: 1.1rem;
    font-weight: 500;
}

.word-count {
    font-size: 0.875rem;
    color: var(--text-secondary);
}

textarea {
    flex-grow: 1;
    background: transparent;
    border: none;
    color: var(--text-primary);
    padding: 1.5rem;
    font-family: inherit;
    font-size: 1rem;
    line-height: 1.6;
    resize: none;
    outline: none;
}

textarea::placeholder {
    color: rgba(255, 255, 255, 0.2);
}

.primary-btn {
    margin: 1.5rem;
    padding: 1rem;
    background: var(--accent);
    color: white;
    border: none;
    border-radius: 8px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease;
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 0.5rem;
}

.primary-btn:hover {
    background: var(--accent-hover);
    transform: translateY(-2px);
    box-shadow: 0 10px 20px rgba(59, 130, 246, 0.3);
}

.primary-btn:disabled {
    opacity: 0.7;
    cursor: not-allowed;
    transform: none;
}

.loader {
    width: 20px;
    height: 20px;
    border: 3px solid rgba(255, 255, 255, 0.3);
    border-radius: 50%;
    border-top-color: white;
    animation: spin 1s ease-in-out infinite;
}

@keyframes spin {
    to {
        transform: rotate(360deg);
    }
}

.hidden {
    display: none !important;
}

.tabs {
    display: flex;
    gap: 1.5rem;
    align-self: stretch;
}

.tab {
    background: transparent;
    border: none;
    color: var(--text-secondary);
    cursor: pointer;
    font-size: 0.9rem;
    font-weight: 500;
    padding: 0;
    position: relative;
    transition: color 0.2s;
    height: 100%;
    display: flex;
    align-items: center;
}

.tab:hover {
    color: var(--text-primary);
}

.tab.active {
    color: var(--text-primary);
}

.tab.active::after {
    content: '';
    position: absolute;
    bottom: -1px;
    left: 0;
    right: 0;
    height: 2px;
    background: var(--accent);
    border-radius: 2px 2px 0 0;
}

.tab-content {
    display: none;
    flex-grow: 1;
    padding: 1.5rem;
    overflow-y: auto;
}

.tab-content.active {
    display: block;
}

.empty-state {
    height: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: var(--text-secondary);
    gap: 1rem;
}

/* ========================
   PROGRESS PANEL (Copyleaks-style)
   ======================== */

.progress-panel {
    height: 100%;
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
}

.progress-header {
    display: flex;
    align-items: center;
    gap: 1rem;
}

.progress-bar-container {
    flex: 1;
    height: 8px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 4px;
    overflow: hidden;
}

.progress-bar-fill {
    height: 100%;
    width: 0%;
    background: linear-gradient(90deg, var(--accent), #8b5cf6);
    border-radius: 4px;
    transition: width 0.8s cubic-bezier(0.1, 0.7, 0.1, 1);
}

.progress-percent {
    font-size: 0.875rem;
    color: var(--text-secondary);
    min-width: 100px;
    text-align: right;
}

.progress-steps {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
}

.progress-step {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 0.75rem 1rem;
    background: rgba(0, 0, 0, 0.2);
    border-radius: 10px;
    border: 1px solid transparent;
    animation: stepFadeIn 0.4s ease forwards;
    opacity: 0;
    transform: translateY(10px);
}

.progress-step.active {
    border-color: var(--accent);
    background: rgba(59, 130, 246, 0.1);
}

.progress-step.done {
    border-color: var(--success);
    opacity: 0.6;
}

@keyframes stepFadeIn {
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.step-icon {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}

.step-icon.active {
    background: rgba(59, 130, 246, 0.2);
}

.step-icon.done {
    background: rgba(16, 185, 129, 0.2);
}

.step-icon .spinner {
    width: 16px;
    height: 16px;
    border: 2px solid rgba(59, 130, 246, 0.3);
    border-top-color: var(--accent);
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
}

.step-icon .check {
    color: var(--success);
    font-size: 14px;
}

.step-text {
    font-size: 0.9rem;
    color: var(--text-primary);
}

/* Skeleton shimmer blocks */
.skeleton-results {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    margin-top: 1rem;
}

.skeleton-block {
    height: 20px;
    background: linear-gradient(90deg, rgba(255, 255, 255, 0.04) 25%, rgba(255, 255, 255, 0.08) 50%, rgba(255, 255, 255, 0.04) 75%);
    background-size: 200% 100%;
    animation: shimmer 1.5s infinite;
    border-radius: 6px;
    width: 100%;
}

.skeleton-block.short {
    width: 75%;
}

.skeleton-block.shorter {
    width: 55%;
}

@keyframes shimmer {
    0% {
        background-position: 200% 0;
    }

    100% {
        background-position: -200% 0;
    }
}

/* ========================
   SCORE + RESULTS
   ======================== */

.score-cards {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
    margin-bottom: 2rem;
}

.score-card {
    background: rgba(0, 0, 0, 0.2);
    padding: 1.25rem;
    border-radius: 12px;
    border: 1px solid rgba(255, 255, 255, 0.05);
}

.score-card h3 {
    font-size: 0.875rem;
    color: var(--text-secondary);
    margin-bottom: 0.5rem;
    font-weight: 500;
}

.score-value {
    font-size: 1.75rem;
    font-weight: 700;
    margin-bottom: 1rem;
}

.score-bar {
    height: 6px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 3px;
    overflow: hidden;
}

.score-bar .fill {
    height: 100%;
    background: var(--accent);
    width: 0%;
    transition: width 1s cubic-bezier(0.1, 0.7, 0.1, 1);
}

.analysis-details {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    background: rgba(0, 0, 0, 0.2);
    padding: 1.5rem;
    border-radius: 12px;
}

.detail-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.badge {
    padding: 0.25rem 0.75rem;
    border-radius: 99px;
    font-size: 0.875rem;
    font-weight: 600;
    background: rgba(255, 255, 255, 0.1);
}

.badge.safe {
    background: rgba(16, 185, 129, 0.2);
    color: var(--success);
}

.badge.risk {
    background: rgba(239, 68, 68, 0.2);
    color: var(--danger);
}

.badge.warn {
    background: rgba(245, 158, 11, 0.2);
    color: var(--warning);
}

.truncate-link {
    color: var(--accent);
    text-decoration: none;
    max-width: 250px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.truncate-link:hover {
    text-decoration: underline;
}

.output-content {
    line-height: 1.8;
    color: #e2e8f0;
}

.output-content p {
    margin-bottom: 1rem;
}

.output-content h1,
.output-content h2 {
    margin: 1.5rem 0 1rem 0;
    color: white;
}

.output-content ul {
    padding-left: 1.5rem;
    margin-bottom: 1rem;
}

/* ========================
   HISTORY
   ======================== */

.history-list {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.history-item {
    background: rgba(0, 0, 0, 0.25);
    padding: 1.25rem;
    border-radius: 12px;
    border: 1px solid rgba(255, 255, 255, 0.05);
    cursor: pointer;
    transition: all 0.2s ease;
}

.history-item:hover {
    border-color: var(--accent);
    background: rgba(59, 130, 246, 0.05);
    transform: translateY(-2px);
}

.history-meta {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.5rem;
}

.history-date {
    font-size: 0.8rem;
    color: var(--text-secondary);
}

.history-score {
    font-size: 0.85rem;
    font-weight: 600;
    padding: 0.2rem 0.6rem;
    border-radius: 6px;
}

.history-score.low {
    background: rgba(16, 185, 129, 0.2);
    color: var(--success);
}

.history-score.mid {
    background: rgba(245, 158, 11, 0.2);
    color: var(--warning);
}

.history-score.high {
    background: rgba(239, 68, 68, 0.2);
    color: var(--danger);
}

.history-preview {
    font-size: 0.85rem;
    color: var(--text-secondary);
    line-height: 1.5;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

/* Toast Notifications */
#toast-container {
    position: fixed;
    bottom: 2rem;
    right: 2rem;
    display: flex;
    flex-direction: column;
    gap: 1rem;
    z-index: 100;
}

.toast {
    background: #1e293b;
    border-left: 4px solid var(--accent);
    padding: 1rem 1.5rem;
    border-radius: 8px;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
    color: white;
    font-size: 0.9rem;
    animation: slideIn 0.3s forwards;
}

.toast.error {
    border-left-color: var(--danger);
}

@keyframes slideIn {
    from {
        transform: translateX(100%);
        opacity: 0;
    }

    to {
        transform: translateX(0);
        opacity: 1;
    }
}
```

### `backend/config.py`

```python
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    
    GOOGLE_CX_ID = os.getenv("GOOGLE_CX_ID")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

```

### `backend/main.py`

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from api.routes import router as api_router
from models.database import init_db
import time

# Initialize DB on boot
init_db()

app = FastAPI(title="CRE SaaS MVP")

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print("CRITICAL ERROR:", str(exc))
    return JSONResponse(
        status_code=500,
        content={"error": str(exc), "status": "failed"}
    )

# Production CORS config
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "https://your-production-domain.com"], # Strict security
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Very basic Rate Limiting (In a real SaaS, use Redis)
request_history = {}
MAX_REQS_PER_MIN = 10

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    # Only limit the heavy AI endpoints
    if "/api/process" in request.url.path:
        client_ip = request.client.host
        current_time = time.time()
        
        if client_ip not in request_history:
            request_history[client_ip] = []
            
        history = request_history[client_ip]
        # Remove timestamps older than 60 seconds
        request_history[client_ip] = [t for t in history if current_time - t < 60]
        
        if len(request_history[client_ip]) >= MAX_REQS_PER_MIN:
            return JSONResponse(status_code=429, content={"message": "Rate limit exceeded. Try again in a minute."})
            
        request_history[client_ip].append(current_time)

    response = await call_next(request)
    return response

app.include_router(api_router, prefix="/api")

# Serve the frontend statically from the root
import os
frontend_dir = os.path.join(os.path.dirname(__file__), "../frontend")
app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

```

### `backend/requirements.txt`

```text
fastapi
uvicorn
python-dotenv
beautifulsoup4
lxml
requests
numpy
scikit-learn
sentence-transformers
duckduckgo-search
trafilatura
google-generativeai
googlesearch-python
gunicorn

```

### `backend/utils/helpers.py`

```python
import uuid

def generate_job_id() -> str:
    """
    Generates a unique job ID for asynchronous processing tasks.
    (Useful when transitioning from synchronous FastAPI to Celery/Redis).
    """
    return uuid.uuid4().hex

def calculate_token_estimate(text: str) -> int:
    """
    Provides a rough 1 token ~= 4 chars estimate for basic cost calculations 
    without needing the heavy tiktoken library.
    """
    if not text:
        return 0
    return len(text) // 4

```

### `backend/utils/logger.py`

```python
import logging
import sys

def get_logger(name: str):
    """
    Standardized logger for the CRE SaaS Backend.
    Provides uniform formatting for console output.
    """
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
    return logger

```

### `backend/utils/text_cleaner.py`

```python
import re
from bs4 import BeautifulSoup

def clean_html_for_db(html_content: str) -> str:
    """
    Sanitizes HTML before storing it in the database.
    Removes potentially malicious script tags while preserving formatting.
    """
    if not html_content:
        return ""
        
    soup = BeautifulSoup(html_content, "lxml")
    
    # Remove script and style tags completely
    for script_or_style in soup(["script", "style"]):
        script_or_style.extract()
        
    return str(soup)

def extract_plain_text(html_content: str) -> str:
    """
    Strips ALL HTML tags to return just raw plain text.
    Useful if needed for token counting.
    """
    soup = BeautifulSoup(html_content, "lxml")
    return soup.get_text(separator=" ", strip=True)

```

### `backend/utils/url_validator.py`

```python
import ipaddress
import socket
from urllib.parse import urlparse

def is_safe_url(url: str) -> bool:
    parsed = urlparse(url)

    if parsed.scheme not in ("http", "https"):
        return False

    if not parsed.hostname:
        return False

    try:
        # 2-second timeout prevents blocking on slow/fresh domains
        old_timeout = socket.getdefaulttimeout()
        socket.setdefaulttimeout(2)
        ip = socket.gethostbyname(parsed.hostname)
        socket.setdefaulttimeout(old_timeout)
        
        ip_obj = ipaddress.ip_address(ip)
        if ip_obj.is_private:
            return False

    except (socket.gaierror, socket.timeout, OSError):
        # DNS failed — still allow the URL (better to try scraping than silently drop)
        return True

    return True

```

### `backend/models/article_model.py`

```python
from pydantic import BaseModel
from typing import Optional

class ArticleInput(BaseModel):
    content: str
    source_url: Optional[str] = None
    
# This model represents the structure in the SQLite DB
class ArticleRecord(BaseModel):
    id: Optional[int]
    original_content: str
    rewritten_content: Optional[str]
    semantic_similarity_score: Optional[str]
    originality_score: Optional[str]
    idea_similarity: Optional[str]
    adsense_safety: Optional[str]

```

### `backend/models/database.py`

```python
import sqlite3
import os
import uuid

DB_PATH = os.path.join(os.path.dirname(__file__), '../../database/cre.db')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # USERS TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        email TEXT UNIQUE NOT NULL,
        api_key TEXT UNIQUE NOT NULL,
        subscription_tier TEXT DEFAULT 'free',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # USAGE TRACKING TABLE (CRITICAL)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usage_tracking (
        id TEXT PRIMARY KEY,
        user_id TEXT,
        words_processed INTEGER DEFAULT 0,
        requests_count INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    # ARTICLES TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS articles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        original_content TEXT,
        rewritten_content TEXT,
        similarity_score REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)
    
    # Insert a dummy admin user for MVP testing
    cursor.execute("SELECT id FROM users WHERE email='admin@cre.com'")
    if not cursor.fetchone():
        admin_id = str(uuid.uuid4())
        cursor.execute(
            "INSERT INTO users (id, email, api_key, subscription_tier) VALUES (?, ?, ?, ?)",
            (admin_id, 'admin@cre.com', 'cre-admin-key-12345', 'enterprise')
        )

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()

```

### `backend/models/report_model.py`

```python
from pydantic import BaseModel
from typing import Optional

class CREReport(BaseModel):
    semantic_similarity: str
    originality_score: str
    idea_similarity: str
    value_addition: str
    adsense_safety: str
    ai_rationale: str
    urls_scanned: int
    top_match_url: Optional[str] = None

```

### `backend/api/auth_middleware.py`

```python
from fastapi import Request, HTTPException
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '../../database/cre.db')

def get_user_from_api_key(api_key: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, email, subscription_tier FROM users WHERE api_key=?",
        (api_key,)
    )

    user = cursor.fetchone()
    conn.close()

    if not user:
        return None

    return {
        "id": user[0],
        "email": user[1],
        "tier": user[2]
    }


async def authenticate_request(request: Request):
    api_key = request.headers.get("X-API-Key")

    if not api_key:
        raise HTTPException(status_code=401, detail="Missing API Key")

    user = get_user_from_api_key(api_key)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    request.state.user = user

```

### `backend/api/controllers.py`

```python
from bs4 import BeautifulSoup
from services.query_generator import generate_search_queries
from services.similarity_service import calculate_similarity
from services.analysis_service import analyze_originality
from services.rewrite_service import rewrite_text_nodes
from services.scoring_service import generate_cre_report
import asyncio
import json
import sqlite3
import os

REWRITE_TAGS = ["p", "li", "h1", "h2", "h3", "h4", "h5", "h6", "blockquote"]
MIN_TEXT_LENGTH = 40
DB_PATH = os.path.join(os.path.dirname(__file__), '../../database/cre.db')


def extract_rewriteable_nodes(html: str):
    soup = BeautifulSoup(html, "lxml")
    nodes = []

    for tag in soup.find_all(REWRITE_TAGS):
        text = tag.get_text(strip=True)
        if not text:
            continue
        if len(text) < MIN_TEXT_LENGTH:
            continue
            
        nodes.append({
            "element": tag,
            "text": text
        })

    return soup, nodes


def save_article_to_db(user_id: str, original: str, rewritten: str, similarity: float):
    """Save processed article to database for history tracking."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO articles (user_id, original_content, rewritten_content, semantic_similarity_score) VALUES (?, ?, ?, ?)",
            (user_id, original[:5000], rewritten[:5000], f"{int(similarity * 100)}%")
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[DB] Failed to save article: {e}")


def get_user_history(user_id: str, limit: int = 20):
    """Retrieve user's processing history."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, original_content, rewritten_content, semantic_similarity_score, created_at FROM articles WHERE user_id=? ORDER BY created_at DESC LIMIT ?",
            (user_id, limit)
        )
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"[DB] History query failed: {e}")
        return []


async def process_article_controller(html_content: str, user_id: str = None, progress_callback=None) -> dict:
    """
    The Ultimate Multi-Model CRE Pipeline (SaaS MVP).
    Now with progress callbacks for live frontend updates.
    """
    import re
    
    # Step 1: Extract text
    if progress_callback:
        await progress_callback("extracting", "Breaking down your text for in-depth analysis...")
    
    if not bool(re.search(r'<(p|div|h[1-6]|li|article|section|blockquote)[^>]*>', html_content, re.IGNORECASE)):
        paragraphs = [p.strip() for p in html_content.split('\n') if p.strip()]
        html_content = "".join([f"<p>{p}</p>" for p in paragraphs])
        
    soup, nodes = extract_rewriteable_nodes(html_content)
    if not nodes:
        return {"status": "skipped", "message": "No rewriteable text found."}
        
    full_text = "\n".join([n["text"] for n in nodes])
    
    # Step 2: Retrieval
    if progress_callback:
        await progress_callback("searching", "Analyzing billions of web pages for matching content...")
    
    from services.retrieval_engine import retrieve_candidate_sources
    references = await retrieve_candidate_sources(full_text, generate_search_queries)
    
    # Step 3: Similarity
    if progress_callback:
        await progress_callback("comparing", "Scanning millions of publications for potential matches...")
    
    top_match, all_scores = await calculate_similarity(full_text, references)
    similarity_score = top_match["score"] if top_match else 0.0
    
    # Step 4: Analysis
    if progress_callback:
        await progress_callback("analyzing", "Ensuring your content is uniquely yours...")
    
    analysis = await analyze_originality(full_text, top_match, similarity_score)
    
    # Step 5: Rewrite
    if progress_callback:
        await progress_callback("rewriting", "Analyzing for advanced rewording and paraphrasing...")
    
    texts_to_rewrite = [n["text"] for n in nodes]
    rewritten_texts = await rewrite_text_nodes(texts_to_rewrite)
    
    for node, new_text in zip(nodes, rewritten_texts):
        node["element"].string = new_text
        
    final_html = str(soup)
    
    # Step 6: Report
    if progress_callback:
        await progress_callback("finalizing", "Generating your comprehensive report...")
    
    report = generate_cre_report(similarity_score, analysis)
    report["urls_scanned"] = len(references)
    if top_match:
        report["top_match_url"] = top_match["url"]

    # Save to DB for history
    if user_id:
        save_article_to_db(user_id, full_text, "\n".join(rewritten_texts), similarity_score)
        
    return {
        "status": "success",
        "report": report,
        "final_html": final_html
    }

```

### `backend/api/routes.py`

```python
from fastapi import APIRouter, Request, Depends
from fastapi.responses import StreamingResponse
from api.controllers import process_article_controller, get_user_history
from pydantic import BaseModel
from api.auth_middleware import authenticate_request
from services.limit_service import enforce_limits
from services.usage_service import track_usage
import asyncio
import json

router = APIRouter()

class ProcessRequest(BaseModel):
    content: str


@router.post("/process")
async def process(req: Request, payload: ProcessRequest, auth=Depends(authenticate_request)):
    user = req.state.user
    content = payload.content

    enforce_limits(user, content)

    result = await process_article_controller(content, user_id=user["id"])

    track_usage(user["id"], len(content.split()))

    return result


@router.post("/process-stream")
async def process_stream(req: Request, payload: ProcessRequest, auth=Depends(authenticate_request)):
    """
    SSE endpoint that streams progress updates to the frontend in real-time.
    Each event contains a step name and a human-readable status message.
    """
    user = req.state.user
    content = payload.content

    enforce_limits(user, content)

    progress_queue = asyncio.Queue()

    async def progress_callback(step: str, message: str):
        await progress_queue.put({"step": step, "message": message})

    async def run_pipeline():
        result = await process_article_controller(content, user_id=user["id"], progress_callback=progress_callback)
        track_usage(user["id"], len(content.split()))
        await progress_queue.put({"step": "complete", "result": result})

    async def event_generator():
        task = asyncio.create_task(run_pipeline())
        
        while True:
            try:
                event = await asyncio.wait_for(progress_queue.get(), timeout=120)
            except asyncio.TimeoutError:
                yield f"data: {json.dumps({'step': 'timeout', 'message': 'Processing timed out'})}\n\n"
                break
            
            yield f"data: {json.dumps(event)}\n\n"
            
            if event.get("step") == "complete":
                break
        
        await task

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.get("/history")
async def get_history(req: Request, auth=Depends(authenticate_request)):
    """Returns the user's past processing history."""
    user = req.state.user
    history = get_user_history(user["id"])
    return {"history": history}

```

### `backend/services/analysis_service.py`

```python
import os
import requests
from config import Config
import json
import asyncio

ANALYSIS_PROMPT = """You are an expert Google AdSense Evaluator.
Evaluate the following user article against the top-matching internet reference article.
The exact vector mathematical similarity score is {sim_pct:.1f}%.

USER ARTICLE:
{article}

TOP REFERENCE (investigating for plagiarism/duplication):
{reference}

Analyze:
1. Idea Similarity (Low, Medium, High)
2. Value Addition (Does the user's article add unique perspectives or examples?)
3. AdSense Risk (Low, Medium, High)

Return ONLY a JSON dictionary with these keys: "idea_similarity", "value_addition", "adsense_risk", "analysis_summary"."""


def _call_openai_compatible(api_url: str, api_key: str, model: str, prompt: str) -> dict:
    """Generic OpenAI-compatible API caller (works for DeepSeek + Groq)."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3
    }
    response = requests.post(api_url, headers=headers, json=payload, timeout=30)
    response.raise_for_status()
    data = response.json()
    content = data["choices"][0]["message"]["content"]
    # Strip markdown code fences if present
    content = content.strip()
    if content.startswith("```json"):
        content = content[7:]
    if content.startswith("```"):
        content = content[3:]
    if content.endswith("```"):
        content = content[:-3]
    return json.loads(content.strip())


async def analyze_originality(article: str, top_reference: dict, similarity_score: float) -> dict:
    """
    CRE Analysis Engine — DeepSeek primary, Groq fallback.
    Uses both to deeply analyze Idea Similarity and Value Addition.
    """
    ref_dict = top_reference or {}
    prompt = ANALYSIS_PROMPT.format(
        sim_pct=similarity_score * 100,
        article=article[:1500],
        reference=ref_dict.get('content', 'No reference article found.')[:1500]
    )

    # Try DeepSeek first
    deepseek_key = Config.DEEPSEEK_API_KEY
    if deepseek_key and "YOUR" not in deepseek_key:
        try:
            print("[Analysis] Trying DeepSeek...")
            result = await asyncio.to_thread(
                _call_openai_compatible,
                "https://api.deepseek.com/v1/chat/completions",
                deepseek_key,
                "deepseek-chat",
                prompt
            )
            print("[Analysis] DeepSeek succeeded")
            return result
        except Exception as e:
            print(f"[Analysis] DeepSeek failed: {e}")

    # Fallback to Groq
    groq_key = Config.GROQ_API_KEY
    if groq_key and "gsk_" in groq_key:
        try:
            print("[Analysis] Trying Groq fallback...")
            result = await asyncio.to_thread(
                _call_openai_compatible,
                "https://api.groq.com/openai/v1/chat/completions",
                groq_key,
                "llama-3.3-70b-versatile",
                prompt
            )
            print("[Analysis] Groq succeeded")
            return result
        except Exception as e:
            print(f"[Analysis] Groq failed: {e}")

    # Fallback to OpenRouter
    openrouter_key = Config.OPENROUTER_API_KEY
    if openrouter_key and "sk-or" in openrouter_key:
        try:
            print("[Analysis] Trying OpenRouter fallback...")
            result = await asyncio.to_thread(
                _call_openai_compatible,
                "https://openrouter.ai/api/v1/chat/completions",
                openrouter_key,
                "meta-llama/llama-3.3-70b-instruct:free",
                prompt
            )
            print("[Analysis] OpenRouter succeeded")
            return result
        except Exception as e:
            print(f"[Analysis] OpenRouter failed: {e}")

    print("[Analysis] All LLMs failed — returning basic analysis")
    return {
        "idea_similarity": "Unknown",
        "value_addition": "Unknown",
        "adsense_risk": "Unknown",
        "analysis_summary": "Analysis unavailable — no LLM API responded."
    }

```

### `backend/services/embedding_service.py`

```python
import numpy as np
import requests
import asyncio
from config import Config

# The Hugging Face feature extraction pipeline URL for the MiniLM model
HF_API_URL = "https://api-inference.huggingface.co/pipeline/feature-extraction/sentence-transformers/all-MiniLM-L6-v2"

# Lazy-loaded local fallback model
_local_model = None

async def generate_embeddings(texts: list[str]) -> np.ndarray:
    """
    Component 4: Embedding Engine
    Takes a list of texts and returns their semantic vector embeddings.
    First tries Hugging Face Serverless API; falls back to local execution.
    """
    hf_key = Config.HUGGINGFACE_API_KEY
    
    def _fetch_hf_api():
        headers = {"Authorization": f"Bearer {hf_key}"}
        response = requests.post(HF_API_URL, headers=headers, json={"inputs": texts})
        response.raise_for_status()
        return np.array(response.json())
        
    def _run_local():
        global _local_model
        if _local_model is None:
            from sentence_transformers import SentenceTransformer
            print("Loading local MiniLM model for embeddings...")
            _local_model = SentenceTransformer('all-MiniLM-L6-v2')
            
        return _local_model.encode(texts, normalize_embeddings=True)
        
    if hf_key and "hf_" in hf_key:
        try:
            return await asyncio.to_thread(_fetch_hf_api)
        except Exception as e:
            print(f"HuggingFace API failed ({e}). Falling back to local model computation...")
            
    # Fallback executing the lightweight local model in the background thread
    return await asyncio.to_thread(_run_local)

```

### `backend/services/limit_service.py`

```python
import os
from fastapi import HTTPException
from services.usage_service import get_daily_usage

FREE_MAX_WORDS = int(os.getenv("FREE_PLAN_MAX_WORDS", 3000))
FREE_MAX_REQ = int(os.getenv("FREE_PLAN_MAX_REQUESTS_PER_DAY", 10))

def enforce_limits(user, text: str):
    words = len(text.split())

    if user["tier"] == "free":
        if words > FREE_MAX_WORDS:
            raise HTTPException(
                status_code=403,
                detail="Word limit exceeded for free plan"
            )

        usage = get_daily_usage(user["id"])

        if usage >= FREE_MAX_REQ:
            raise HTTPException(
                status_code=429,
                detail="Daily request limit exceeded"
            )

```

### `backend/services/query_generator.py`

```python
import google.generativeai as genai
from config import Config
import json

genai.configure(api_key=Config.GEMINI_API_KEY)

# Use Gemini 2.0 Flash — highest free-tier limit (1500 RPD)
model = genai.GenerativeModel('gemini-2.0-flash')

async def generate_search_queries(article_text: str, num_queries: int = 3) -> list[str]:
    """
    Extracts the core themes of an article and generates targeted search queries
    to find similar content on the internet.
    """
    # Truncate text just in case it's massive to save tokens
    preview_text = article_text[:2000]
    
    prompt = f"""
    Analyze the following article text and generate exactly {num_queries} specific, highly relevant Google search queries that would lead someone to an article with exactly the same content or ideas.
    
    Output the queries as a valid JSON array of strings. Do not include markdown formatting or ANY other text, just the raw JSON array like this: ["query 1", "query 2", "query 3"]
    
    ARTICLE TEXT:
    {preview_text}
    """
    
    try:
        import asyncio
        response = await asyncio.to_thread(
            model.generate_content,
            prompt
        )
        text_response = response.text.strip().replace("```json", "").replace("```", "")
        queries = json.loads(text_response)
        if isinstance(queries, list):
            return queries
        return [queries] if isinstance(queries, str) else []
    except Exception as e:
        print(f"Error generating queries: {e}")
        return []

```

### `backend/services/retrieval_engine.py`

```python
import re
import asyncio
import requests
from bs4 import BeautifulSoup
from services.scraper_service import scrape_urls
from utils.url_validator import is_safe_url

# ==============================
# 1. Fingerprint Extractor
# ==============================

def extract_fingerprints(text: str, max_fingerprints=8):
    """
    Extract exact phrases from the article for plagiarism search.
    Uses sentence-based extraction (60-200 chars) as primary strategy.
    
    CRITICAL: Do NOT wrap in quotes — googlesearch-python returns 0 for quoted queries.
    CRITICAL: Preserve hyphens/slashes — stripping turns Scikit-Learn into Scikit Learn.
    """
    # Only strip newlines and tabs, preserve all other punctuation
    clean_text = re.sub(r'[\n\t\r]+', ' ', text)
    clean_text = re.sub(r'\s+', ' ', clean_text).strip()
    
    # Split on sentence boundaries
    sentences = re.split(r'[.!?]', clean_text)
    
    fingerprints = []
    for s in sentences:
        s = s.strip()
        if len(s) < 60 or len(s) > 200:
            continue
        # Raw unquoted phrase — search engines naturally rank exact matches higher
        fingerprints.append(s)
        if len(fingerprints) >= max_fingerprints:
            break
    
    # If not enough sentence-based fingerprints, add sliding window fingerprints
    if len(fingerprints) < 3:
        words = clean_text.split()
        for i in range(0, max(1, len(words) - 8 + 1), 20):
            chunk = words[i:i+8]
            if len(chunk) < 5:
                continue
            fingerprints.append(" ".join(chunk))
            if len(fingerprints) >= max_fingerprints:
                break
    
    return fingerprints


# ==============================
# 2. Semantic Query Generator Fusion
# ==============================

async def fuse_queries(article_text, semantic_generator):
    """Combines fingerprint queries + semantic queries."""
    fingerprints = extract_fingerprints(article_text)
    semantic_queries = await semantic_generator(article_text)
    return list(set(fingerprints + semantic_queries))


# ==============================
# 3. Multi-Engine Retrieval
# ==============================

async def search_ddg_html(queries):
    """
    Uses DuckDuckGo's HTML endpoint directly.
    The duckduckgo_search pip library is dead (returns [] for everything).
    The HTML POST endpoint works reliably.
    """
    urls = set()
    headers = {"User-Agent": "Mozilla/5.0"}
    
    def _search():
        import time
        for q in queries:
            try:
                resp = requests.post(
                    "https://html.duckduckgo.com/html/",
                    data={"q": q},
                    headers=headers,
                    timeout=10
                )
                soup = BeautifulSoup(resp.text, "html.parser")
                for a in soup.select("a.result__url"):
                    link = a.get("href")
                    if link and link.startswith("http") and is_safe_url(link):
                        urls.add(link)
                time.sleep(0.5)  # Rate limit protection
            except Exception as e:
                print(f"DDG HTML error: {e}")
    
    await asyncio.to_thread(_search)
    return list(urls)


async def search_google(queries):
    """
    Uses googlesearch-python (scrapes Google).
    This is the engine that successfully retrieved amanxai.com at 85% similarity.
    """
    urls = set()
    
    def _search():
        try:
            from googlesearch import search
            for q in queries:
                try:
                    for url in search(q, num_results=5, lang="en"):
                        if is_safe_url(url):
                            urls.add(url)
                except Exception as e:
                    print(f"Google search error on query: {e}")
        except ImportError:
            print("googlesearch-python not installed")
    
    await asyncio.to_thread(_search)
    return list(urls)


async def search_bing(queries):
    """
    Bing HTML scraper — best-effort fallback.
    Often CAPTCHA-blocked but worth trying.
    """
    urls = set()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    def _search():
        for q in queries:
            try:
                resp = requests.get(
                    f"https://www.bing.com/search?q={q}",
                    headers=headers,
                    timeout=10
                )
                soup = BeautifulSoup(resp.text, "html.parser")
                for a in soup.find_all("a", href=True):
                    link = a["href"]
                    if link.startswith("http") and "bing.com" not in link and "microsoft.com" not in link:
                        if is_safe_url(link):
                            urls.add(link)
            except Exception:
                pass
    
    await asyncio.to_thread(_search)
    return list(urls)


# ==============================
# 4. URL Ranking Engine
# ==============================

def rank_urls(urls, article_text):
    """Rank URLs based on domain quality + keyword overlap."""
    keywords = set(article_text.lower().split()[:50])
    ranked = []
    
    for url in urls:
        score = 0
        url_lower = url.lower()
        for k in keywords:
            if k in url_lower:
                score += 1
        if any(x in url_lower for x in ["blog", "article", "post"]):
            score += 3
        ranked.append((url, score))
    
    ranked.sort(key=lambda x: x[1], reverse=True)
    return [u[0] for u in ranked]


# ==============================
# 5. Adaptive Scraping Controller
# ==============================

async def adaptive_scrape(urls, max_scrape=5):
    """Scrapes highest ranked URLs first."""
    scraped = []
    for url in urls[:max_scrape]:
        try:
            data = await scrape_urls([url])
            if data:
                scraped.extend(data)
        except:
            pass
    return scraped


# ==============================
# 6. Master Retrieval Pipeline
# ==============================

async def retrieve_candidate_sources(article_text, semantic_generator):
    # Step 1: Query fusion
    queries = await fuse_queries(article_text, semantic_generator)
    print("\n[RETRIEVAL] Queries:", queries)

    # Step 2: Multi-engine search (all run, results merged)
    ddg_urls = await search_ddg_html(queries)
    google_urls = await search_google(queries)
    bing_urls = await search_bing(queries)
    
    all_urls = list(set(ddg_urls + google_urls + bing_urls))
    print(f"[RETRIEVAL] URLs found: DDG={len(ddg_urls)} Google={len(google_urls)} Bing={len(bing_urls)} Total={len(all_urls)}")

    # Step 3: Ranking
    ranked_urls = rank_urls(all_urls, article_text)
    print(f"[RETRIEVAL] Top candidates: {ranked_urls[:5]}")

    # Step 4: Adaptive scrape
    scraped = await adaptive_scrape(ranked_urls)
    print(f"[RETRIEVAL] Scraped sources: {len(scraped)}")

    return scraped

```

### `backend/services/rewrite_service.py`

```python
import google.generativeai as genai
from config import Config
import asyncio
import json
import requests

genai.configure(api_key=Config.GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')


def _rewrite_via_groq(texts: list[str]) -> list[str]:
    """Groq fallback using llama-3.3-70b-versatile (14,400 free RPD)."""
    groq_key = Config.GROQ_API_KEY
    if not groq_key:
        return texts
    
    input_json = json.dumps({str(i): text for i, text in enumerate(texts)})
    prompt = f"""Rewrite the following blocks of text in a completely original, human-sounding way.
Keep the same structural meaning, but ensure high uniqueness.

You MUST output a valid JSON array of strings in the exact same order as the input.
I am providing {len(texts)} blocks. I expect exactly a JSON list of length {len(texts)}.

INPUT:
{input_json}"""

    headers = {
        "Authorization": f"Bearer {groq_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }
    
    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers=headers,
        json=payload,
        timeout=30
    )
    response.raise_for_status()
    data = response.json()
    content = data["choices"][0]["message"]["content"].strip()
    
    # Strip markdown fences
    if content.startswith("```json"):
        content = content[7:]
    if content.startswith("```"):
        content = content[3:]
    if content.endswith("```"):
        content = content[:-3]
    
    rewritten = json.loads(content.strip())
    if isinstance(rewritten, list) and len(rewritten) == len(texts):
        return [str(item) for item in rewritten]
    return texts


async def rewrite_text_nodes(texts: list[str]) -> list[str]:
    """
    Rewrite Engine — Gemini primary, Groq fallback.
    Takes text nodes, rewrites them for uniqueness, returns same-length array.
    """
    if not texts:
        return []

    input_json = json.dumps({str(i): text for i, text in enumerate(texts)})
    
    prompt = f"""Rewrite the following blocks of text in a completely original, human-sounding way.
Keep the same structural meaning, but ensure high uniqueness.

You MUST output a valid JSON array of strings in the exact same order as the input.
I am providing {len(texts)} blocks. I expect exactly a JSON list of length {len(texts)}.

INPUT:
{input_json}"""

    # Try Gemini first (2 attempts)
    for attempt in range(2):
        try:
            response = await asyncio.to_thread(
                model.generate_content,
                prompt,
                generation_config={"response_mime_type": "application/json"}
            )
            
            result_text = response.text.strip()
            rewritten_array = json.loads(result_text)
            
            if isinstance(rewritten_array, list) and len(rewritten_array) == len(texts):
                print("[Rewrite] Gemini succeeded")
                return [str(item) for item in rewritten_array]
            else:
                print(f"[Rewrite] Gemini length mismatch: expected {len(texts)}, got {len(rewritten_array)}")
        except Exception as e:
            print(f"[Rewrite] Gemini error (attempt {attempt+1}): {e}")
            
        await asyncio.sleep(2)
    
    # Fallback to Groq
    try:
        print("[Rewrite] Trying Groq fallback...")
        result = await asyncio.to_thread(_rewrite_via_groq, texts)
        if result != texts:
            print("[Rewrite] Groq succeeded")
            return result
    except Exception as e:
        print(f"[Rewrite] Groq fallback failed: {e}")
    
    # Fallback to OpenRouter
    try:
        openrouter_key = Config.OPENROUTER_API_KEY
        if openrouter_key and "sk-or" in openrouter_key:
            print("[Rewrite] Trying OpenRouter fallback...")
            headers = {
                "Authorization": f"Bearer {openrouter_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "meta-llama/llama-3.3-70b-instruct:free",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7
            }
            resp = await asyncio.to_thread(
                requests.post,
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            resp.raise_for_status()
            content = resp.json()["choices"][0]["message"]["content"].strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            rewritten = json.loads(content.strip())
            if isinstance(rewritten, list) and len(rewritten) == len(texts):
                print("[Rewrite] OpenRouter succeeded")
                return [str(item) for item in rewritten]
    except Exception as e:
        print(f"[Rewrite] OpenRouter fallback failed: {e}")
    
    print("[Rewrite] All engines failed. Returning originals.")
    return texts

```

### `backend/services/scoring_service.py`

```python
def generate_cre_report(similarity_score: float, deepseek_analysis: dict) -> dict:
    """
    Component 8: CRE Scoring Engine
    Aggregates the math and the LLM reasoning to produce the final comprehensive report.
    """
    # Inverse the mathematical similarity to get an originality integer
    originality_score = max(0, int((1.0 - similarity_score) * 100))
    sem_sim_percent = int(similarity_score * 100)
    
    # Calculate a rough /10 trust score based on AI logic
    risk = deepseek_analysis.get("adsense_risk", "Unknown").lower()
    trust = 9 if risk == "low" else (5 if risk == "medium" else 2)
    if sem_sim_percent > 40: trust -= 2
    trust = max(1, trust)

    report = {
        "similarity_score": f"{sem_sim_percent}%",
        "originality_score": f"{originality_score}%",
        "trust_score": f"{trust}/10",
        "idea_similarity": deepseek_analysis.get("idea_similarity", "Unknown"),
        "value_addition": deepseek_analysis.get("value_addition", "Unknown"),
        "adsense_safety": deepseek_analysis.get("adsense_risk", "Unknown"),
        "ai_rationale": deepseek_analysis.get("analysis_summary", "No rationale generated.")
    }
    
    return report

```

### `backend/services/scraper_service.py`

```python
import trafilatura
import asyncio
from utils.url_validator import is_safe_url

async def scrape_urls(urls: list[str]) -> list[dict]:
    """
    Component 3: Content Scraper Engine
    Takes a list of URLs and uses trafilatura to extract raw, clean article text 
    (stripping ads, navbars, and boilerplate).
    Returns a list of dictionaries with url and content.
    """
    scraped_data = []

    def _scrape_single(url):
        # SSRF Protection: Prevent scanning localhost or private API networks
        if not is_safe_url(url):
            print(f"Skipping dangerous URL target: {url}")
            return None
            
        try:
            downloaded = trafilatura.fetch_url(url)
            if downloaded:
                # include_links=False keeps the text purely semantic
                text = trafilatura.extract(downloaded, include_links=False, include_images=False)
                print(f"Scraped {url}, length={len(text) if text else 0}")
                if text and len(text) > 200: # Only keep substantial articles
                    return {"url": url, "content": text}
        except Exception as e:
            print(f"Trafilatura Scrape Error for {url}: {e}")
        return None

    # Run scrapes concurrently
    loop = asyncio.get_running_loop()
    tasks = [
        loop.run_in_executor(None, _scrape_single, url)
        for url in urls
    ]
    
    results = await asyncio.gather(*tasks)
    
    # Filter out None results
    for r in results:
        if r:
            scraped_data.append(r)
            
    return scraped_data

```

### `backend/services/search_service.py`

```python
import requests
from config import Config
import asyncio

async def search_internet(queries: list[str], max_results_per_query: int = 3) -> list[str]:
    """
    Component 2: Internet Retrieval Engine
    Takes a list of search queries and returns a deduplicated list of URLs.
    Uses official Google Custom Search API for production reliability.
    """
    urls = set()
    
    api_key = Config.GOOGLE_API_KEY
    cx = Config.GOOGLE_CX_ID
    
    def _search_google():
        for query in queries:
            try:
                url = f"https://customsearch.googleapis.com/customsearch/v1?cx={cx}&q={query}&key={api_key}&num={max_results_per_query}"
                response = requests.get(url)
                response.raise_for_status()
                data = response.json()
                for item in data.get("items", []):
                    urls.add(item.get("link"))
            except Exception as e:
                print(f"Google Search Error for '{query}': {e}")
                
    def _search_ddg_fallback():
        from duckduckgo_search import DDGS
        print("Falling back to DuckDuckGo Search...")
        with DDGS() as ddgs:
            for query in queries:
                try:
                    results = ddgs.text(query, max_results=max_results_per_query)
                    if results:
                        for r in results:
                            urls.add(r.get('href'))
                except Exception as e:
                    print(f"DDGS Search Error for query '{query}': {e}")

    # Use Google API if keys exist, otherwise DDG
    if api_key and cx and "AIza" in api_key:
        await asyncio.to_thread(_search_google)
        
    # If Google failed (e.g. 403 Forbidden) or keys don't exist, fallback to DDG
    if not urls:
        await asyncio.to_thread(_search_ddg_fallback)
        
    return list(urls)

```

### `backend/services/similarity_service.py`

```python
from sklearn.metrics.pairwise import cosine_similarity
from services.embedding_service import generate_embeddings
import numpy as np
import re

def _chunk_text(text: str, chunk_size: int = 300) -> list[str]:
    """Splits text into chunks of roughly `chunk_size` words."""
    words = text.split()
    return [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]

async def calculate_similarity(user_article: str, reference_articles: list[dict]) -> tuple[dict, list[dict]]:
    """
    Component 5: Chunk-Based Similarity Engine
    Calculates the exact math-based cosine similarity between the user's article
    and the scraped internet references.
    
    Uses paragraph-level chunking to detect localized plagiarism and prevent score dilution.
    """
    if not reference_articles:
        return None, []
        
    user_chunks = _chunk_text(user_article)
    
    scored_references = []
    
    # We will compute each reference independently against all user chunks
    for ref in reference_articles:
        ref_chunks = _chunk_text(ref["content"])
        if not ref_chunks: continue
        
        # We need embeddings for all user_chunks + all ref_chunks
        texts_to_embed = user_chunks + ref_chunks
        embeddings = await generate_embeddings(texts_to_embed)
        
        user_vectors = embeddings[:len(user_chunks)]
        ref_vectors = embeddings[len(user_chunks):]
        
        # Calculate O(N x M) similarity matrix
        similarity_matrix = cosine_similarity(user_vectors, ref_vectors)
        
        # Find the absolute highest similarity between ANY user chunk and ANY reference chunk
        max_score = float(np.max(similarity_matrix))
        
        print(f"Similarity Matrix Math: {ref['url']} scored {max_score:.4f}")
        
        scored_references.append({
            "url": ref["url"],
            "score": max_score,
            "content": ref["content"] # Pass this back so the Analysis service can read it
        })
        
    # Sort descending
    scored_references.sort(key=lambda x: x["score"], reverse=True)
    
    highest_match = scored_references[0] if scored_references else None
    
    return highest_match, scored_references

```

### `backend/services/usage_service.py`

```python
import sqlite3
import uuid
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), '../../database/cre.db')


def track_usage(user_id: str, words: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO usage_tracking (id, user_id, words_processed, requests_count)
        VALUES (?, ?, ?, 1)
    """, (
        str(uuid.uuid4()),
        user_id,
        words
    ))

    conn.commit()
    conn.close()


def get_daily_usage(user_id: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT SUM(requests_count)
        FROM usage_tracking
        WHERE user_id=?
        AND date(created_at)=date('now')
    """, (user_id,))

    result = cursor.fetchone()
    conn.close()

    return result[0] if result[0] else 0

```

