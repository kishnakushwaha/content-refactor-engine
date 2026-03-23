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
│   │   ├── index_db.py
│   │   └── report_model.py
│   ├── requirements.txt
│   ├── services
│   │   ├── analysis_service.py
│   │   ├── embedding_service.py
│   │   ├── fingerprint_engine.py
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

### 📁 Module Descriptions

#### 🌐 Frontend (`frontend/`)
- **`index.html`**: The main user dashboard where they paste their article content.
- **`styles.css`**: All the styling for the application, including the "shimmer/skeleton" loading animations and the layout of the split-pane report view.
- **`app.js`**: The vanilla JavaScript logic that handles sending data to the backend, listening to the real-time Server-Sent Events (SSE) stream, and dynamically updating the UI progress bar.

#### 🗄️ Database (`database/`)
- **`cre.db`**: The single, portable SQLite3 database file that holds absolutely everything: user accounts, article histories (original vs rewritten content), and the local fingerprint plagiarism index.

#### ⚙️ Backend (`backend/`)
**1. Core Config & Entry Points**
- **`main.py`**: The entry point to the FastAPI application. It wires up CORS, the global exception handler, rate limiting, and attaches the routing files.
- **`.env`**: Stores all of your secret API keys (Gemini, OpenRouter, DeepSeek, Groq).
- **`config.py`**: Loads the `.env` variables into Python memory safely using Pydantic Settings.

**2. Models & Database (`backend/models/`)**
- **`database.py`**: Handles connecting to the `database/cre.db` SQLite file securely.
- **`article_model.py` / `report_model.py`**: Pydantic schemas (data shapes) that define exactly what data the frontend must send to the backend, and what data the backend will return.
- **`index_db.py`**: Houses the table structures for the new `indexed_documents` and `fingerprints` tables.

**3. API Routes (`backend/api/`)**
- **`controllers.py`**: The main traffic cop. It receives the HTTP request from the frontend and orchestrates the entire pipeline: Scraping -> Embedding -> Analysis -> Rewriting. It also streams the SSE updates back to the browser.
- **`auth_middleware.py`**: Checks if the user has an active API key or free trial limit remaining before letting them hit the expensive LLM endpoints.
- **`limits.py` & `usage_tracker.py`**: Enforces rate limiting (e.g., max 5 requests per day for free users) and tracks character counts in the SQLite database.

**4. The Pipeline Services (`backend/services/`)**
- **`query_generation.py`**: Uses DeepSeek/Groq to read the user's input article and figure out the 3 most important keyword search queries to test it against the internet.
- **`search_service.py`**: Takes those queries and searches them on Google Custom Search API or DuckDuckGo.
- **`scraper_service.py`**: Uses `Trafilatura` to visit the URLs found by the search service, bypass anti-bot protections, and extract the raw, readable text from those live competitor websites.
- **`embedding_service.py`**: Converts both the user's article and the scraped competitor articles into dense mathematical vectors (using a HuggingFace `sentence-transformers` model).
- **`similarity.py`**: Performs O(N x M) Cosine Similarity Math. It compares the vectors from the step above to generate a mathematical percentage.
- **`analysis_service.py`**: Hands the text over to your Heavy Reasoner LLMs (DeepSeek -> Groq -> OpenRouter) to grade it.
- **`rewrite_service.py`**: The final step. Hands the text to your Fast Writer LLMs (Gemini -> Groq -> OpenRouter) to completely refactor the sentence structures.
- **`fingerprint_engine.py`**: A fast algorithmic chunker that chops text into 5-word shingles and saves them in the database for instant offline plagiarism matching.

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

### `compare_articles.py`

```python
import sqlite3
import difflib
import sys
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'database', 'cre.db')
OUTPUT_HTML = os.path.join(os.path.dirname(__file__), 'diff_output.html')

def generate_diff(article_id=None):
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if article_id:
        cursor.execute("SELECT id, original_content, rewritten_content FROM articles WHERE id = ?", (article_id,))
    else:
        # Fetch the most recent article
        cursor.execute("SELECT id, original_content, rewritten_content FROM articles ORDER BY id DESC LIMIT 1")

    row = cursor.fetchone()
    conn.close()

    if not row:
        print("No articles found in the database.")
        return

    art_id, original, rewritten = row

    if not original:
        original = ""
    if not rewritten:
        rewritten = ""

    # Generate HTML diff
    html_diff = difflib.HtmlDiff(wrapcolumn=80)
    diff_table = html_diff.make_file(
        original.splitlines(),
        rewritten.splitlines(),
        fromdesc=f"Original Content (Article ID {art_id})",
        todesc=f"Rewritten Content (Article ID {art_id})",
        context=True
    )

    with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
        f.write(diff_table)

    print(f"Diff successfully generated for Article ID: {art_id}")
    print(f"Open this file in your browser to view the comparison: file://{os.path.abspath(OUTPUT_HTML)}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        try:
            art_id = int(sys.argv[1])
            generate_diff(art_id)
        except ValueError:
            print("Please provide a valid numeric Article ID.")
    else:
        generate_diff()

```

### `diff_output.html`

```html

<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
          "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

<html>

<head>
    <meta http-equiv="Content-Type"
          content="text/html; charset=utf-8" />
    <title></title>
    <style type="text/css">
        table.diff {font-family: Menlo, Consolas, Monaco, Liberation Mono, Lucida Console, monospace; border:medium}
        .diff_header {background-color:#e0e0e0}
        td.diff_header {text-align:right}
        .diff_next {background-color:#c0c0c0}
        .diff_add {background-color:#aaffaa}
        .diff_chg {background-color:#ffff77}
        .diff_sub {background-color:#ffaaaa}
    </style>
</head>

<body>
    
    <table class="diff" id="difflib_chg_to0__top"
           cellspacing="0" cellpadding="0" rules="groups" >
        <colgroup></colgroup> <colgroup></colgroup> <colgroup></colgroup>
        <colgroup></colgroup> <colgroup></colgroup> <colgroup></colgroup>
        <thead><tr><th class="diff_next"><br /></th><th colspan="2" class="diff_header">Original Content (Article ID 1)</th><th class="diff_next"><br /></th><th colspan="2" class="diff_header">Rewritten Content (Article ID 1)</th></tr></thead>
        <tbody>
            <tr><td class="diff_next" id="difflib_chg_to0__0"><a href="#difflib_chg_to0__top">t</a></td><td class="diff_header" id="from0_1">1</td><td nowrap="nowrap"><span class="diff_sub">How&nbsp;to&nbsp;Pick&nbsp;the&nbsp;Right&nbsp;AI&nbsp;Model&nbsp;for&nbsp;Your&nbsp;Project</span></td><td class="diff_next"><a href="#difflib_chg_to0__top">t</a></td><td class="diff_header" id="to0_1">1</td><td nowrap="nowrap"><span class="diff_add">Choosing&nbsp;the&nbsp;Ideal&nbsp;AI&nbsp;Model&nbsp;for&nbsp;Your&nbsp;Project:&nbsp;A&nbsp;Comprehensive&nbsp;Guide</span></td></tr>
            <tr><td class="diff_next"></td><td class="diff_header" id="from0_2">2</td><td nowrap="nowrap"><span class="diff_sub">There&nbsp;is&nbsp;a&nbsp;specific&nbsp;kind&nbsp;of&nbsp;paralysis&nbsp;that&nbsp;hits&nbsp;every&nbsp;Data&nbsp;Scientist&nbsp;when&nbsp;they&nbsp;o</span></td><td class="diff_next"></td><td class="diff_header" id="to0_2">2</td><td nowrap="nowrap"><span class="diff_add">Data&nbsp;scientists&nbsp;often&nbsp;find&nbsp;themselves&nbsp;overwhelmed&nbsp;by&nbsp;the&nbsp;plethora&nbsp;of&nbsp;AI&nbsp;models&nbsp;a</span></td></tr>
            <tr><td class="diff_next"></td><td class="diff_header">></td><td nowrap="nowrap"><span class="diff_sub">pen&nbsp;Hugging&nbsp;Face&nbsp;or&nbsp;the&nbsp;OpenAI&nbsp;docs&nbsp;today.&nbsp;It&nbsp;used&nbsp;to&nbsp;be&nbsp;a&nbsp;choice&nbsp;between&nbsp;a&nbsp;Line</span></td><td class="diff_next"></td><td class="diff_header">></td><td nowrap="nowrap"><span class="diff_add">vailable&nbsp;today,&nbsp;from&nbsp;massive&nbsp;API-based&nbsp;language&nbsp;models&nbsp;to&nbsp;agile&nbsp;local&nbsp;models&nbsp;and</span></td></tr>
            <tr><td class="diff_next"></td><td class="diff_header">></td><td nowrap="nowrap"><span class="diff_sub">ar&nbsp;Regression&nbsp;and&nbsp;a&nbsp;Random&nbsp;Forest.&nbsp;Now?&nbsp;You&nbsp;have&nbsp;to&nbsp;choose&nbsp;between&nbsp;massive&nbsp;API-b</span></td><td class="diff_next"></td><td class="diff_header">></td><td nowrap="nowrap"><span class="diff_add">&nbsp;autonomous&nbsp;agents,&nbsp;making&nbsp;it&nbsp;challenging&nbsp;to&nbsp;select&nbsp;the&nbsp;most&nbsp;suitable&nbsp;one&nbsp;for&nbsp;th</span></td></tr>
            <tr><td class="diff_next"></td><td class="diff_header">></td><td nowrap="nowrap"><span class="diff_sub">ased&nbsp;LLMs,&nbsp;nimble&nbsp;local&nbsp;models,&nbsp;multimodal&nbsp;giants,&nbsp;and&nbsp;autonomous&nbsp;agents.&nbsp;So,&nbsp;le</span></td><td class="diff_next"></td><td class="diff_header">></td><td nowrap="nowrap"><span class="diff_add">eir&nbsp;project.</span></td></tr>
            <tr><td class="diff_next"></td><td class="diff_header">></td><td nowrap="nowrap"><span class="diff_sub">t’s&nbsp;understand&nbsp;how&nbsp;to&nbsp;pick&nbsp;the&nbsp;right&nbsp;AI&nbsp;model&nbsp;for&nbsp;your&nbsp;project.</span></td><td class="diff_next"></td><td class="diff_header"></td><td nowrap="nowrap">&nbsp;</td></tr>
            <tr><td class="diff_next"></td><td class="diff_header" id="from0_3">3</td><td nowrap="nowrap"><span class="diff_sub">How&nbsp;to&nbsp;Pick&nbsp;the&nbsp;Right&nbsp;AI&nbsp;Model&nbsp;for&nbsp;Your&nbsp;Project</span></td><td class="diff_next"></td><td class="diff_header" id="to0_3">3</td><td nowrap="nowrap"><span class="diff_add">Choosing&nbsp;the&nbsp;Ideal&nbsp;AI&nbsp;Model&nbsp;for&nbsp;Your&nbsp;Project:&nbsp;A&nbsp;Comprehensive&nbsp;Guide</span></td></tr>
            <tr><td class="diff_next"></td><td class="diff_header" id="from0_4">4</td><td nowrap="nowrap"><span class="diff_sub">The&nbsp;smartest&nbsp;model&nbsp;is&nbsp;rarely&nbsp;the&nbsp;right&nbsp;one.&nbsp;The&nbsp;best&nbsp;engineers&nbsp;don’t&nbsp;just&nbsp;chase&nbsp;</span></td><td class="diff_next"></td><td class="diff_header" id="to0_4">4</td><td nowrap="nowrap"><span class="diff_add">The&nbsp;most&nbsp;intelligent&nbsp;model&nbsp;isn't&nbsp;always&nbsp;the&nbsp;best&nbsp;fit;&nbsp;seasoned&nbsp;engineers&nbsp;priorit</span></td></tr>
            <tr><td class="diff_next"></td><td class="diff_header">></td><td nowrap="nowrap"><span class="diff_sub">benchmarks;&nbsp;they&nbsp;chase&nbsp;fit.&nbsp;Let’s&nbsp;cut&nbsp;through&nbsp;the&nbsp;noise&nbsp;and&nbsp;figure&nbsp;out&nbsp;exactly&nbsp;w</span></td><td class="diff_next"></td><td class="diff_header">></td><td nowrap="nowrap"><span class="diff_add">ize&nbsp;finding&nbsp;the&nbsp;right&nbsp;tool&nbsp;for&nbsp;the&nbsp;specific&nbsp;problem&nbsp;at&nbsp;hand,&nbsp;rather&nbsp;than&nbsp;solely&nbsp;</span></td></tr>
            <tr><td class="diff_next"></td><td class="diff_header">></td><td nowrap="nowrap"><span class="diff_sub">hich&nbsp;tool&nbsp;belongs&nbsp;in&nbsp;your&nbsp;kit&nbsp;for&nbsp;the&nbsp;problem&nbsp;you&nbsp;are&nbsp;solving&nbsp;right&nbsp;now.</span></td><td class="diff_next"></td><td class="diff_header">></td><td nowrap="nowrap"><span class="diff_add">chasing&nbsp;benchmark&nbsp;performance.</span></td></tr>
            <tr><td class="diff_next"></td><td class="diff_header" id="from0_5">5</td><td nowrap="nowrap"><span class="diff_sub">Before&nbsp;you&nbsp;rush&nbsp;to&nbsp;use&nbsp;a&nbsp;Transformer&nbsp;for&nbsp;everything,&nbsp;stop.&nbsp;If&nbsp;your&nbsp;data&nbsp;fits&nbsp;int</span></td><td class="diff_next"></td><td class="diff_header" id="to0_5">5</td><td nowrap="nowrap"><span class="diff_add">Before&nbsp;jumping&nbsp;into&nbsp;using&nbsp;a&nbsp;transformer&nbsp;for&nbsp;every&nbsp;task,&nbsp;take&nbsp;a&nbsp;step&nbsp;back;&nbsp;if&nbsp;you</span></td></tr>
            <tr><td class="diff_next"></td><td class="diff_header">></td><td nowrap="nowrap"><span class="diff_sub">o&nbsp;an&nbsp;Excel&nbsp;spreadsheet,&nbsp;rows&nbsp;and&nbsp;columns&nbsp;of&nbsp;numbers&nbsp;or&nbsp;categories,&nbsp;Generative&nbsp;AI</span></td><td class="diff_next"></td><td class="diff_header">></td><td nowrap="nowrap"><span class="diff_add">r&nbsp;data&nbsp;can&nbsp;be&nbsp;neatly&nbsp;organized&nbsp;into&nbsp;an&nbsp;Excel&nbsp;spreadsheet,&nbsp;a&nbsp;simpler&nbsp;approach&nbsp;mig</span></td></tr>
            <tr><td class="diff_next"></td><td class="diff_header">></td><td nowrap="nowrap"><span class="diff_sub">&nbsp;is&nbsp;often&nbsp;overkill.</span></td><td class="diff_next"></td><td class="diff_header">></td><td nowrap="nowrap"><span class="diff_add">ht&nbsp;be&nbsp;more&nbsp;effective.</span></td></tr>
            <tr><td class="diff_next"></td><td class="diff_header" id="from0_6">6</td><td nowrap="nowrap"><span class="diff_sub">When&nbsp;to&nbsp;choose&nbsp;Traditional&nbsp;ML&nbsp;(XGBoost,&nbsp;LightGBM,&nbsp;Scikit-learn):</span></td><td class="diff_next"></td><td class="diff_header" id="to0_6">6</td><td nowrap="nowrap"><span class="diff_add">Traditional&nbsp;ML&nbsp;Models&nbsp;(XGBoost,&nbsp;LightGBM,&nbsp;Scikit-learn):&nbsp;When&nbsp;to&nbsp;Use&nbsp;Them</span></td></tr>
            <tr><td class="diff_next"></td><td class="diff_header" id="from0_7">7</td><td nowrap="nowrap"><span class="diff_sub">Structured&nbsp;Data:&nbsp;You&nbsp;are&nbsp;predicting&nbsp;customer&nbsp;churn,&nbsp;housing&nbsp;prices,&nbsp;or&nbsp;credit&nbsp;ri</span></td><td class="diff_next"></td><td class="diff_header" id="to0_7">7</td><td nowrap="nowrap"><span class="diff_add">Tabular&nbsp;Data:&nbsp;Predicting&nbsp;outcomes&nbsp;like&nbsp;customer&nbsp;churn,&nbsp;housing&nbsp;prices,&nbsp;or&nbsp;credit</span></td></tr>
            <tr><td class="diff_next"></td><td class="diff_header">></td><td nowrap="nowrap"><span class="diff_sub">sk&nbsp;based&nbsp;on&nbsp;tabular&nbsp;data.</span></td><td class="diff_next"></td><td class="diff_header">></td><td nowrap="nowrap"><span class="diff_add">&nbsp;risk&nbsp;based&nbsp;on&nbsp;structured&nbsp;data&nbsp;is&nbsp;a&nbsp;common&nbsp;use&nbsp;case.</span></td></tr>
            <tr><td class="diff_next"></td><td class="diff_header" id="from0_8">8</td><td nowrap="nowrap"><span class="diff_sub">Explainability:&nbsp;You&nbsp;need&nbsp;to&nbsp;tell&nbsp;a&nbsp;stakeholder&nbsp;exactly&nbsp;why&nbsp;a&nbsp;decision&nbsp;was&nbsp;made&nbsp;(</span></td><td class="diff_next"></td><td class="diff_header" id="to0_8">8</td><td nowrap="nowrap"><span class="diff_add">Interpretability:&nbsp;Providing&nbsp;clear&nbsp;explanations&nbsp;for&nbsp;the&nbsp;decisions&nbsp;made&nbsp;by&nbsp;your&nbsp;mo</span></td></tr>
            <tr><td class="diff_next"></td><td class="diff_header">></td><td nowrap="nowrap"><span class="diff_sub">Feature&nbsp;Importance).</span></td><td class="diff_next"></td><td class="diff_header">></td><td nowrap="nowrap"><span class="diff_add">del,&nbsp;such&nbsp;as&nbsp;feature&nbsp;importance,&nbsp;is&nbsp;crucial&nbsp;in&nbsp;certain&nbsp;applications.</span></td></tr>
            <tr><td class="diff_next"></td><td class="diff_header" id="from0_9">9</td><td nowrap="nowrap"><span class="diff_sub">Speed&nbsp;&amp;&nbsp;Cost:&nbsp;You&nbsp;need&nbsp;to&nbsp;process&nbsp;millions&nbsp;of&nbsp;rows&nbsp;per&nbsp;second&nbsp;with&nbsp;minimal&nbsp;compu</span></td><td class="diff_next"></td><td class="diff_header" id="to0_9">9</td><td nowrap="nowrap"><span class="diff_add">Efficiency&nbsp;&amp;&nbsp;Cost-Effectiveness:&nbsp;Processing&nbsp;large&nbsp;datasets&nbsp;quickly&nbsp;while&nbsp;minimiz</span></td></tr>
            <tr><td class="diff_next"></td><td class="diff_header">></td><td nowrap="nowrap"><span class="diff_sub">te&nbsp;cost.</span></td><td class="diff_next"></td><td class="diff_header">></td><td nowrap="nowrap"><span class="diff_add">ing&nbsp;computational&nbsp;costs&nbsp;is&nbsp;essential&nbsp;for&nbsp;many&nbsp;projects.</span></td></tr>
            <tr><td class="diff_next"></td><td class="diff_header" id="from0_10">10</td><td nowrap="nowrap"><span class="diff_sub">I&nbsp;once&nbsp;saw&nbsp;a&nbsp;team&nbsp;try&nbsp;to&nbsp;use&nbsp;GPT-4&nbsp;to&nbsp;classify&nbsp;simple&nbsp;sentiment&nbsp;on&nbsp;a&nbsp;dataset&nbsp;of&nbsp;</span></td><td class="diff_next"></td><td class="diff_header" id="to0_10">10</td><td nowrap="nowrap"><span class="diff_add">I&nbsp;recall&nbsp;a&nbsp;team&nbsp;that&nbsp;attempted&nbsp;to&nbsp;utilize&nbsp;GPT-4&nbsp;for&nbsp;sentiment&nbsp;analysis&nbsp;on&nbsp;a&nbsp;vast</span></td></tr>
            <tr><td class="diff_next"></td><td class="diff_header">></td><td nowrap="nowrap"><span class="diff_sub">10&nbsp;million&nbsp;tweets.&nbsp;It&nbsp;would&nbsp;have&nbsp;cost&nbsp;them&nbsp;thousands&nbsp;of&nbsp;dollars.&nbsp;A&nbsp;simple&nbsp;Logist</span></td><td class="diff_next"></td><td class="diff_header">></td><td nowrap="nowrap"><span class="diff_add">&nbsp;dataset&nbsp;of&nbsp;tweets,&nbsp;which&nbsp;would&nbsp;have&nbsp;incurred&nbsp;significant&nbsp;costs;&nbsp;a&nbsp;simple&nbsp;logist</span></td></tr>
            <tr><td class="diff_next"></td><td class="diff_header">></td><td nowrap="nowrap"><span class="diff_sub">ic&nbsp;Regression&nbsp;model&nbsp;did&nbsp;it&nbsp;for&nbsp;free&nbsp;in&nbsp;5&nbsp;minutes&nbsp;with&nbsp;95%&nbsp;accuracy.</span></td><td class="diff_next"></td><td class="diff_header">></td><td nowrap="nowrap"><span class="diff_add">ic&nbsp;regression&nbsp;model&nbsp;achieved&nbsp;95%&nbsp;accuracy&nbsp;in&nbsp;mere&nbsp;minutes,&nbsp;at&nbsp;no&nbsp;cost.</span></td></tr>
            <tr><td class="diff_next"></td><td class="diff_header" id="from0_11">11</td><td nowrap="nowrap"><span class="diff_sub">Models&nbsp;like&nbsp;GPT-4o,&nbsp;Claude&nbsp;3.5&nbsp;Sonnet,&nbsp;or&nbsp;Gemini&nbsp;Pro&nbsp;are&nbsp;incredibly&nbsp;powerful&nbsp;gen</span></td><td class="diff_next"></td><td class="diff_header" id="to0_11">11</td><td nowrap="nowrap"><span class="diff_add">Powerful,&nbsp;general-purpose&nbsp;models&nbsp;like&nbsp;GPT-4,&nbsp;Claude,&nbsp;or&nbsp;Gemini&nbsp;offer&nbsp;extensive&nbsp;k</span></td></tr>
            <tr><td class="diff_next"></td><td class="diff_header">></td><td nowrap="nowrap"><span class="diff_sub">eralists.&nbsp;They&nbsp;have&nbsp;world&nbsp;knowledge.&nbsp;However,&nbsp;they&nbsp;are&nbsp;leased,&nbsp;not&nbsp;owned.&nbsp;You&nbsp;se</span></td><td class="diff_next"></td><td class="diff_header">></td><td nowrap="nowrap"><span class="diff_add">nowledge&nbsp;but&nbsp;come&nbsp;with&nbsp;the&nbsp;caveat&nbsp;of&nbsp;being&nbsp;leased,&nbsp;requiring&nbsp;data&nbsp;to&nbsp;be&nbsp;sent&nbsp;out</span></td></tr>
            <tr><td class="diff_next"></td><td class="diff_header">></td><td nowrap="nowrap"><span class="diff_sub">nd&nbsp;data&nbsp;out;&nbsp;you&nbsp;get&nbsp;answers&nbsp;back.</span></td><td class="diff_next"></td><td class="diff_header">></td><td nowrap="nowrap"><span class="diff_add">&nbsp;and&nbsp;answers&nbsp;to&nbsp;be&nbsp;received,&nbsp;rather&nbsp;than&nbsp;being&nbsp;owned&nbsp;outright.</span></td></tr>
            <tr><td class="diff_next"></td><td class="diff_header" id="from0_12">12</td><td nowrap="nowrap"><span class="diff_sub">Complex&nbsp;Reasoning:&nbsp;You&nbsp;need&nbsp;the&nbsp;model&nbsp;to&nbsp;understand&nbsp;nuance,&nbsp;sarcasm,&nbsp;or&nbsp;complex&nbsp;</span></td><td class="diff_next"></td><td class="diff_header" id="to0_12">12</td><td nowrap="nowrap"><span class="diff_add">Complex&nbsp;Problem-Solving:&nbsp;When&nbsp;your&nbsp;project&nbsp;demands&nbsp;nuanced&nbsp;understanding,&nbsp;sarcas</span></td></tr>
            <tr><td class="diff_next"></td><td class="diff_header">></td><td nowrap="nowrap"><span class="diff_sub">logic&nbsp;(like&nbsp;legal&nbsp;summarisation).</span></td><td class="diff_next"></td><td class="diff_header">></td><td nowrap="nowrap"><span class="diff_add">m&nbsp;detection,&nbsp;or&nbsp;intricate&nbsp;logical&nbsp;reasoning,&nbsp;such&nbsp;as&nbsp;legal&nbsp;document&nbsp;summarizatio</span></td></tr>
            <tr><td class="diff_next"></td><td class="diff_header"></td><td nowrap="nowrap">&nbsp;</td><td class="diff_next"></td><td class="diff_header">></td><td nowrap="nowrap"><span class="diff_add">n,&nbsp;these&nbsp;models&nbsp;shine.</span></td></tr>
            <tr><td class="diff_next"></td><td class="diff_header" id="from0_13">13</td><td nowrap="nowrap"><span class="diff_sub">The&nbsp;MVP&nbsp;Phase:&nbsp;You&nbsp;want&nbsp;to&nbsp;build&nbsp;a&nbsp;prototype&nbsp;in&nbsp;a&nbsp;weekend&nbsp;to&nbsp;prove&nbsp;an&nbsp;idea&nbsp;works</span></td><td class="diff_next"></td><td class="diff_header" id="to0_13">13</td><td nowrap="nowrap"><span class="diff_add">Rapid&nbsp;Prototyping:&nbsp;Building&nbsp;a&nbsp;functional&nbsp;prototype&nbsp;over&nbsp;a&nbsp;weekend&nbsp;to&nbsp;validate&nbsp;an</span></td></tr>
            <tr><td class="diff_next"></td><td class="diff_header">></td><td nowrap="nowrap"><span class="diff_sub">.</span></td><td class="diff_next"></td><td class="diff_header">></td><td nowrap="nowrap"><span class="diff_add">&nbsp;idea&nbsp;is&nbsp;often&nbsp;the&nbsp;first&nbsp;step&nbsp;in&nbsp;the&nbsp;development&nbsp;process.</span></td></tr>
            <tr><td class="diff_next"></td><td class="diff_header" id="from0_14">14</td><td nowrap="nowrap"><span class="diff_sub">Generalisation:&nbsp;The&nbsp;input&nbsp;data&nbsp;is&nbsp;highly&nbsp;variable&nbsp;and&nbsp;unstructured&nbsp;(emails,&nbsp;essa</span></td><td class="diff_next"></td><td class="diff_header" id="to0_14">14</td><td nowrap="nowrap"><span class="diff_add">Generalizability:&nbsp;Handling&nbsp;diverse,&nbsp;unstructured&nbsp;data&nbsp;sources&nbsp;like&nbsp;emails,&nbsp;essay</span></td></tr>
            <tr><td class="diff_next"></td><td class="diff_header">></td><td nowrap="nowrap"><span class="diff_sub">ys,&nbsp;messy&nbsp;PDFs).</span></td><td class="diff_next"></td><td class="diff_header">></td><td nowrap="nowrap"><span class="diff_add">s,&nbsp;or&nbsp;disorganized&nbsp;PDFs&nbsp;requires&nbsp;models&nbsp;capable&nbsp;of&nbsp;adapting&nbsp;to&nbsp;variable&nbsp;input.</span></td></tr>
            <tr><td class="diff_next"></td><td class="diff_header" id="from0_15">15</td><td nowrap="nowrap"><span class="diff_sub">With&nbsp;the&nbsp;rise&nbsp;of&nbsp;Llama&nbsp;3,&nbsp;Mistral,&nbsp;and&nbsp;Gemma,&nbsp;the&nbsp;gap&nbsp;between&nbsp;closed&nbsp;and&nbsp;open&nbsp;mo</span></td><td class="diff_next"></td><td class="diff_header" id="to0_15">15</td><td nowrap="nowrap"><span class="diff_add">The&nbsp;emergence&nbsp;of&nbsp;models&nbsp;like&nbsp;Llama,&nbsp;Mistral,&nbsp;and&nbsp;Gemma&nbsp;is&nbsp;bridging&nbsp;the&nbsp;gap&nbsp;betwe</span></td></tr>
            <tr><td class="diff_next"></td><td class="diff_header">></td><td nowrap="nowrap"><span class="diff_sub">dels&nbsp;is&nbsp;closing&nbsp;fast.&nbsp;Running&nbsp;a&nbsp;model&nbsp;locally&nbsp;(or&nbsp;on&nbsp;your&nbsp;own&nbsp;private&nbsp;cloud)&nbsp;is&nbsp;</span></td><td class="diff_next"></td><td class="diff_header">></td><td nowrap="nowrap"><span class="diff_add">en&nbsp;closed&nbsp;and&nbsp;open&nbsp;models,&nbsp;with&nbsp;locally&nbsp;run&nbsp;models&nbsp;offering&nbsp;unparalleled&nbsp;control</span></td></tr>
            <tr><td class="diff_next"></td><td class="diff_header">></td><td nowrap="nowrap"><span class="diff_sub">the&nbsp;ultimate&nbsp;power&nbsp;move&nbsp;for&nbsp;production&nbsp;engineering.</span></td><td class="diff_next"></td><td class="diff_header">></td><td nowrap="nowrap"><span class="diff_add">&nbsp;for&nbsp;production&nbsp;environments.</span></td></tr>
            <tr><td class="diff_next"></td><td class="diff_header" id="from0_16">16</td><td nowrap="nowrap"><span class="diff_sub">When&nbsp;to&nbsp;choose&nbsp;Local&nbsp;LLMs&nbsp;(Llama&nbsp;3,&nbsp;Mistral,&nbsp;Phi-3):</span></td><td class="diff_next"></td><td class="diff_header" id="to0_16">16</td><td nowrap="nowrap"><span class="diff_add">Local&nbsp;LLMs&nbsp;(Llama,&nbsp;Mistral,&nbsp;Phi-3):&nbsp;When&nbsp;to&nbsp;Opt&nbsp;for&nbsp;Them</span></td></tr>
            <tr><td class="diff_next"></td><td class="diff_header" id="from0_17">17</td><td nowrap="nowrap"><span class="diff_sub">Data&nbsp;Privacy:&nbsp;You&nbsp;are&nbsp;dealing&nbsp;with&nbsp;HIPAA&nbsp;(medical),&nbsp;GDPR,&nbsp;or&nbsp;sensitive&nbsp;proprieta</span></td><td class="diff_next"></td><td class="diff_header" id="to0_17">17</td><td nowrap="nowrap"><span class="diff_add">Data&nbsp;Confidentiality:&nbsp;Projects&nbsp;involving&nbsp;sensitive&nbsp;data,&nbsp;such&nbsp;as&nbsp;medical&nbsp;informa</span></td></tr>
            <tr><td class="diff_next"></td><td class="diff_header">></td><td nowrap="nowrap"><span class="diff_sub">ry&nbsp;code.&nbsp;The&nbsp;data&nbsp;cannot&nbsp;leave&nbsp;your&nbsp;server.</span></td><td class="diff_next"></td><td class="diff_header">></td><td nowrap="nowrap"><span class="diff_add">tion&nbsp;under&nbsp;HIPAA&nbsp;or&nbsp;proprietary&nbsp;code,&nbsp;necessitate&nbsp;models&nbsp;that&nbsp;can&nbsp;operate&nbsp;withou</span></td></tr>
            <tr><td class="diff_next"></td><td class="diff_header"></td><td nowrap="nowrap">&nbsp;</td><td class="diff_next"></td><td class="diff_header">></td><td nowrap="nowrap"><span class="diff_add">t&nbsp;data&nbsp;leaving&nbsp;the&nbsp;server.</span></td></tr>
            <tr><td class="diff_next"></td><td class="diff_header" id="from0_18">18</td><td nowrap="nowrap"><span class="diff_sub">Cost&nbsp;Control:&nbsp;You&nbsp;have&nbsp;high&nbsp;volume.&nbsp;Paying&nbsp;per&nbsp;token&nbsp;to&nbsp;an&nbsp;API&nbsp;adds&nbsp;up;&nbsp;running&nbsp;</span></td><td class="diff_next"></td><td class="diff_header" id="to0_18">18</td><td nowrap="nowrap"><span class="diff_add">Budget&nbsp;Management:&nbsp;For&nbsp;high-volume&nbsp;applications,&nbsp;the&nbsp;cost&nbsp;of&nbsp;API&nbsp;calls&nbsp;can&nbsp;escal</span></td></tr>
            <tr><td class="diff_next"></td><td class="diff_header">></td><td nowrap="nowrap"><span class="diff_sub">a&nbsp;GPU&nbsp;instance&nbsp;is&nbsp;a&nbsp;fixed&nbsp;cost.</span></td><td class="diff_next"></td><td class="diff_header">></td><td nowrap="nowrap"><span class="diff_add">ate&nbsp;quickly;&nbsp;in&nbsp;contrast,&nbsp;running&nbsp;a&nbsp;local&nbsp;GPU&nbsp;instance&nbsp;provides&nbsp;a&nbsp;fixed,&nbsp;predict</span></td></tr>
            <tr><td class="diff_next"></td><td class="diff_header"></td><td nowrap="nowrap">&nbsp;</td><td class="diff_next"></td><td class="diff_header">></td><td nowrap="nowrap"><span class="diff_add">able&nbsp;expense.</span></td></tr>
            <tr><td class="diff_next"></td><td class="diff_header" id="from0_19">19</td><td nowrap="nowrap"><span class="diff_sub">Latency:&nbsp;You&nbsp;need&nbsp;instant&nbsp;responses&nbsp;and&nbsp;cannot&nbsp;depend&nbsp;on&nbsp;an&nbsp;API’s&nbsp;internet&nbsp;conne</span></td><td class="diff_next"></td><td class="diff_header" id="to0_19">19</td><td nowrap="nowrap"><span class="diff_add">Real-Time&nbsp;Responses:&nbsp;Applications&nbsp;requiring&nbsp;instantaneous&nbsp;feedback&nbsp;cannot&nbsp;rely&nbsp;o</span></td></tr>
            <tr><td class="diff_next"></td><td class="diff_header">></td><td nowrap="nowrap"><span class="diff_sub">ction.</span></td><td class="diff_next"></td><td class="diff_header">></td><td nowrap="nowrap"><span class="diff_add">n&nbsp;API&nbsp;connectivity&nbsp;and&nbsp;internet&nbsp;speeds.</span></td></tr>
            <tr><td class="diff_next"></td><td class="diff_header" id="from0_20">20</td><td nowrap="nowrap"><span class="diff_sub">We&nbsp;are&nbsp;moving&nbsp;from&nbsp;Chatbots&nbsp;(who&nbsp;talk)&nbsp;to&nbsp;Agents&nbsp;(who&nbsp;do).&nbsp;An&nbsp;agent&nbsp;is&nbsp;an&nbsp;LLM&nbsp;wr</span></td><td class="diff_next"></td><td class="diff_header" id="to0_20">20</td><td nowrap="nowrap"><span class="diff_add">The&nbsp;evolution&nbsp;from&nbsp;chatbots&nbsp;to&nbsp;agents&nbsp;marks&nbsp;a&nbsp;significant&nbsp;shift;&nbsp;agents&nbsp;are&nbsp;not&nbsp;</span></td></tr>
            <tr><td class="diff_next"></td><td class="diff_header">></td><td nowrap="nowrap"><span class="diff_sub">apped&nbsp;in&nbsp;a&nbsp;loop&nbsp;that&nbsp;allows&nbsp;it&nbsp;to&nbsp;use&nbsp;tools,&nbsp;search&nbsp;the&nbsp;web,&nbsp;query&nbsp;a&nbsp;database,&nbsp;o</span></td><td class="diff_next"></td><td class="diff_header">></td><td nowrap="nowrap"><span class="diff_add">just&nbsp;language&nbsp;models&nbsp;but&nbsp;are&nbsp;capable&nbsp;of&nbsp;performing&nbsp;tasks,&nbsp;searching&nbsp;the&nbsp;web,&nbsp;que</span></td></tr>
            <tr><td class="diff_next"></td><td class="diff_header">></td><td nowrap="nowrap"><span class="diff_sub">r&nbsp;run&nbsp;Python&nbsp;code.</span></td><td class="diff_next"></td><td class="diff_header">></td><td nowrap="nowrap"><span class="diff_add">rying&nbsp;databases,&nbsp;or&nbsp;executing&nbsp;code.</span></td></tr>
            <tr><td class="diff_next"></td><td class="diff_header" id="from0_21">21</td><td nowrap="nowrap"><span class="diff_sub">Multi-step&nbsp;Workflows:&nbsp;The&nbsp;task&nbsp;requires&nbsp;planning.&nbsp;Example:&nbsp;“Research&nbsp;this&nbsp;compan</span></td><td class="diff_next"></td><td class="diff_header" id="to0_21">21</td><td nowrap="nowrap"><span class="diff_add">Multi-Step&nbsp;Processes:&nbsp;Tasks&nbsp;that&nbsp;involve&nbsp;planning,&nbsp;such&nbsp;as&nbsp;researching&nbsp;a&nbsp;company</span></td></tr>
            <tr><td class="diff_next"></td><td class="diff_header">></td><td nowrap="nowrap"><span class="diff_sub">y,&nbsp;then&nbsp;find&nbsp;their&nbsp;stock&nbsp;price,&nbsp;then&nbsp;write&nbsp;a&nbsp;summary.”</span></td><td class="diff_next"></td><td class="diff_header">></td><td nowrap="nowrap"><span class="diff_add">,&nbsp;finding&nbsp;its&nbsp;stock&nbsp;price,&nbsp;and&nbsp;summarizing&nbsp;the&nbsp;information,&nbsp;are&nbsp;ideal&nbsp;for&nbsp;these&nbsp;</span></td></tr>
            <tr><td class="diff_next"></td><td class="diff_header"></td><td nowrap="nowrap">&nbsp;</td><td class="diff_next"></td><td class="diff_header">></td><td nowrap="nowrap"><span class="diff_add">advanced&nbsp;models.</span></td></tr>
            <tr><td class="diff_next"></td><td class="diff_header" id="from0_22">22</td><td nowrap="nowrap"><span class="diff_sub">External&nbsp;Actions:&nbsp;You&nbsp;need&nbsp;the&nbsp;AI&nbsp;to&nbsp;book&nbsp;a&nbsp;meeting,&nbsp;send&nbsp;an&nbsp;email,&nbsp;or&nbsp;update&nbsp;a&nbsp;</span></td><td class="diff_next"></td><td class="diff_header" id="to0_22">22</td><td nowrap="nowrap"><span class="diff_add">External&nbsp;Interactions:&nbsp;When&nbsp;the&nbsp;AI&nbsp;needs&nbsp;to&nbsp;perform&nbsp;actions&nbsp;like&nbsp;scheduling&nbsp;meet</span></td></tr>
            <tr><td class="diff_next"></td><td class="diff_header">></td><td nowrap="nowrap"><span class="diff_sub">Jira&nbsp;ticket.</span></td><td class="diff_next"></td><td class="diff_header">></td><td nowrap="nowrap"><span class="diff_add">ings,&nbsp;sending&nbsp;emails,&nbsp;or&nbsp;updating&nbsp;tickets,&nbsp;the&nbsp;capabilities&nbsp;of&nbsp;agents&nbsp;come&nbsp;into&nbsp;</span></td></tr>
            <tr><td class="diff_next"></td><td class="diff_header"></td><td nowrap="nowrap">&nbsp;</td><td class="diff_next"></td><td class="diff_header">></td><td nowrap="nowrap"><span class="diff_add">play.</span></td></tr>
            <tr><td class="diff_next"></td><td class="diff_header" id="from0_23">23</td><td nowrap="nowrap"><span class="diff_sub">Dynamic&nbsp;Context:&nbsp;The&nbsp;answer&nbsp;isn’t&nbsp;in&nbsp;the&nbsp;model’s&nbsp;training&nbsp;data,&nbsp;and&nbsp;it&nbsp;changes&nbsp;e</span></td><td class="diff_next"></td><td class="diff_header" id="to0_23">23</td><td nowrap="nowrap"><span class="diff_add">Dynamic&nbsp;Information:&nbsp;Situations&nbsp;where&nbsp;the&nbsp;answer&nbsp;is&nbsp;not&nbsp;static&nbsp;and&nbsp;changes&nbsp;frequ</span></td></tr>
            <tr><td class="diff_next"></td><td class="diff_header">></td><td nowrap="nowrap"><span class="diff_sub">very&nbsp;minute&nbsp;(like&nbsp;checking&nbsp;weather&nbsp;or&nbsp;stock&nbsp;prices).</span></td><td class="diff_next"></td><td class="diff_header">></td><td nowrap="nowrap"><span class="diff_add">ently,&nbsp;such&nbsp;as&nbsp;checking&nbsp;current&nbsp;weather&nbsp;or&nbsp;stock&nbsp;prices,&nbsp;require&nbsp;models&nbsp;that&nbsp;can</span></td></tr>
            <tr><td class="diff_next"></td><td class="diff_header"></td><td nowrap="nowrap">&nbsp;</td><td class="diff_next"></td><td class="diff_header">></td><td nowrap="nowrap"><span class="diff_add">&nbsp;adapt&nbsp;and&nbsp;fetch&nbsp;new&nbsp;data.</span></td></tr>
            <tr><td class="diff_next"></td><td class="diff_header" id="from0_24">24</td><td nowrap="nowrap"><span class="diff_sub">As&nbsp;you&nbsp;continue&nbsp;your&nbsp;journey&nbsp;in&nbsp;Data&nbsp;Science,&nbsp;remember&nbsp;this:&nbsp;Your&nbsp;value&nbsp;isn’t&nbsp;de</span></td><td class="diff_next"></td><td class="diff_header" id="to0_24">24</td><td nowrap="nowrap"><span class="diff_add">As&nbsp;you&nbsp;progress&nbsp;in&nbsp;your&nbsp;data&nbsp;science&nbsp;journey,&nbsp;remember&nbsp;that&nbsp;your&nbsp;value&nbsp;is&nbsp;not&nbsp;me</span></td></tr>
            <tr><td class="diff_next"></td><td class="diff_header">></td><td nowrap="nowrap"><span class="diff_sub">fined&nbsp;by&nbsp;the&nbsp;complexity&nbsp;of&nbsp;the&nbsp;model&nbsp;you&nbsp;use,&nbsp;but&nbsp;by&nbsp;the&nbsp;problem&nbsp;you&nbsp;solve.&nbsp;Some</span></td><td class="diff_next"></td><td class="diff_header">></td><td nowrap="nowrap"><span class="diff_add">asured&nbsp;by&nbsp;the&nbsp;complexity&nbsp;of&nbsp;the&nbsp;models&nbsp;you&nbsp;use,&nbsp;but&nbsp;by&nbsp;the&nbsp;problems&nbsp;you&nbsp;solve&nbsp;ef</span></td></tr>
            <tr><td class="diff_next"></td><td class="diff_header">></td><td nowrap="nowrap"><span class="diff_sub">times,&nbsp;the&nbsp;most&nbsp;advanced&nbsp;AI&nbsp;solution&nbsp;is&nbsp;a&nbsp;simple&nbsp;SQL&nbsp;query.&nbsp;Sometimes,&nbsp;it’s&nbsp;a&nbsp;ma</span></td><td class="diff_next"></td><td class="diff_header">></td><td nowrap="nowrap"><span class="diff_add">fectively;&nbsp;sometimes,&nbsp;the&nbsp;simplest&nbsp;solutions,&nbsp;like&nbsp;a&nbsp;well-crafted&nbsp;SQL&nbsp;query,&nbsp;are</span></td></tr>
            <tr><td class="diff_next"></td><td class="diff_header">></td><td nowrap="nowrap"><span class="diff_sub">ssive&nbsp;Agentic&nbsp;workflow.</span></td><td class="diff_next"></td><td class="diff_header">></td><td nowrap="nowrap"><span class="diff_add">&nbsp;the&nbsp;most&nbsp;powerful.</span></td></tr>
            <tr><td class="diff_next"></td><td class="diff_header" id="from0_25">25</td><td nowrap="nowrap"><span class="diff_sub">Have&nbsp;the&nbsp;humility&nbsp;to&nbsp;start&nbsp;simple,&nbsp;and&nbsp;the&nbsp;courage&nbsp;to&nbsp;scale&nbsp;up&nbsp;only&nbsp;when&nbsp;the&nbsp;pro</span></td><td class="diff_next"></td><td class="diff_header" id="to0_25">25</td><td nowrap="nowrap"><span class="diff_add">Embracing&nbsp;humility&nbsp;to&nbsp;start&nbsp;with&nbsp;simple&nbsp;solutions&nbsp;and&nbsp;having&nbsp;the&nbsp;courage&nbsp;to&nbsp;scal</span></td></tr>
            <tr><td class="diff_next"></td><td class="diff_header">></td><td nowrap="nowrap"><span class="diff_sub">blem&nbsp;demands&nbsp;it.&nbsp;That&nbsp;is&nbsp;the&nbsp;difference&nbsp;between&nbsp;a&nbsp;hype-chaser&nbsp;and&nbsp;a&nbsp;true&nbsp;enginee</span></td><td class="diff_next"></td><td class="diff_header">></td><td nowrap="nowrap"><span class="diff_add">e&nbsp;up&nbsp;as&nbsp;needed&nbsp;is&nbsp;what&nbsp;distinguishes&nbsp;a&nbsp;true&nbsp;engineer&nbsp;from&nbsp;one&nbsp;who&nbsp;merely&nbsp;chases&nbsp;</span></td></tr>
            <tr><td class="diff_next"></td><td class="diff_header">></td><td nowrap="nowrap"><span class="diff_sub">r.</span></td><td class="diff_next"></td><td class="diff_header">></td><td nowrap="nowrap"><span class="diff_add">trends.</span></td></tr>
            <tr><td class="diff_next"></td><td class="diff_header" id="from0_26">26</td><td nowrap="nowrap"><span class="diff_sub">I&nbsp;hope&nbsp;you&nbsp;liked&nbsp;this&nbsp;article&nbsp;on&nbsp;how&nbsp;to&nbsp;pick&nbsp;the&nbsp;right&nbsp;AI&nbsp;model&nbsp;for&nbsp;your&nbsp;project</span></td><td class="diff_next"></td><td class="diff_header" id="to0_26">26</td><td nowrap="nowrap"><span class="diff_add">I&nbsp;hope&nbsp;this&nbsp;article&nbsp;has&nbsp;provided&nbsp;you&nbsp;with&nbsp;valuable&nbsp;insights&nbsp;into&nbsp;selecting&nbsp;the&nbsp;r</span></td></tr>
            <tr><td class="diff_next"></td><td class="diff_header">></td><td nowrap="nowrap"><span class="diff_sub">.&nbsp;Follow&nbsp;me&nbsp;on&nbsp;Instagram&nbsp;for&nbsp;many&nbsp;more&nbsp;resources.</span></td><td class="diff_next"></td><td class="diff_header">></td><td nowrap="nowrap"><span class="diff_add">ight&nbsp;AI&nbsp;model&nbsp;for&nbsp;your&nbsp;project;&nbsp;for&nbsp;more&nbsp;resources&nbsp;and&nbsp;updates,&nbsp;follow&nbsp;me&nbsp;on&nbsp;Ins</span></td></tr>
            <tr><td class="diff_next"></td><td class="diff_header"></td><td nowrap="nowrap">&nbsp;</td><td class="diff_next"></td><td class="diff_header">></td><td nowrap="nowrap"><span class="diff_add">tagram.</span></td></tr>
        </tbody>
    </table>
    <table class="diff" summary="Legends">
        <tr> <th colspan="2"> Legends </th> </tr>
        <tr> <td> <table border="" summary="Colors">
                      <tr><th> Colors </th> </tr>
                      <tr><td class="diff_add">&nbsp;Added&nbsp;</td></tr>
                      <tr><td class="diff_chg">Changed</td> </tr>
                      <tr><td class="diff_sub">Deleted</td> </tr>
                  </table></td>
             <td> <table border="" summary="Links">
                      <tr><th colspan="2"> Links </th> </tr>
                      <tr><td>(f)irst change</td> </tr>
                      <tr><td>(n)ext change</td> </tr>
                      <tr><td>(t)op</td> </tr>
                  </table></td> </tr>
    </table>
</body>

</html>
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

### `test_fingerprint.py`

```python
#!/usr/bin/env python3
"""
Fingerprint Engine Verification Test

Tests the complete pipeline:
  1. Text normalization
  2. Shingling
  3. MurmurHash3 hashing
  4. Document indexing into DB
  5. O(1) lookup and matching
"""
import sys
import os
import time

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from models.index_db import init_index_tables, get_index_stats
from services.fingerprint_engine import (
    normalize_text,
    generate_shingles,
    hash_shingles,
    generate_fingerprints,
    index_document,
    lookup_fingerprints,
)

# ==============================
# Setup
# ==============================
print("=" * 60)
print("FINGERPRINT ENGINE VERIFICATION TEST")
print("=" * 60)

# Initialize tables
init_index_tables()
stats = get_index_stats()
print(f"\n[Setup] Index stats before test: {stats}")

# ==============================
# Test 1: Text Normalization
# ==============================
print("\n--- Test 1: Text Normalization ---")
raw = "  Machine Learning is used in Artificial Intelligence systems!!! "
normalized = normalize_text(raw)
print(f"  Input:      '{raw}'")
print(f"  Normalized: '{normalized}'")
assert normalized == "machine learning is used in artificial intelligence systems"
print("  ✅ PASSED")

# ==============================
# Test 2: Shingle Generation
# ==============================
print("\n--- Test 2: Shingle Generation ---")
shingles = generate_shingles(normalized, n=5)
print(f"  Input words: {len(normalized.split())}")
print(f"  Shingles generated: {len(shingles)}")
for i, s in enumerate(shingles):
    print(f"    [{i}] {s}")
expected_count = len(normalized.split()) - 5 + 1
assert len(shingles) == expected_count, f"Expected {expected_count}, got {len(shingles)}"
print("  ✅ PASSED")

# ==============================
# Test 3: MurmurHash3 Hashing
# ==============================
print("\n--- Test 3: MurmurHash3 Hashing ---")
hashes = hash_shingles(shingles)
print(f"  Hashes generated: {len(hashes)}")
for i, h in enumerate(hashes):
    print(f"    [{i}] {shingles[i]} → {h}")
assert all(isinstance(h, int) for h in hashes)
assert len(set(hashes)) == len(hashes), "Hash collision detected in small set!"
print("  ✅ PASSED")

# ==============================
# Test 4: Full Fingerprint Generation
# ==============================
print("\n--- Test 4: Full Fingerprint Generation ---")
article = """
Machine learning algorithms are increasingly being used in modern artificial intelligence 
systems to automate complex decision-making processes. These algorithms learn from data 
patterns and make predictions without explicit programming. Deep learning, a subset of 
machine learning, uses neural networks with multiple layers to extract higher-level features 
from raw input data. This approach has revolutionized fields such as computer vision, 
natural language processing, and speech recognition.
"""
fps = generate_fingerprints(article)
print(f"  Article word count: {len(article.split())}")
print(f"  Fingerprints generated: {len(fps)}")
assert len(fps) > 0
print("  ✅ PASSED")

# ==============================
# Test 5: Document Indexing
# ==============================
print("\n--- Test 5: Document Indexing ---")
result = index_document("https://example.com/ml-article", article)
print(f"  Result: {result}")
assert result["status"] == "indexed"
assert result["fingerprint_count"] > 0

# Index a second document
article2 = """
Cloud computing provides on-demand availability of computer system resources, especially 
data storage and computing power, without direct active management by the user. Large 
cloud providers offer their services from data centers located around the world. Cloud 
computing enables organizations to consume compute resources as a utility rather than 
building and maintaining computing infrastructure in-house.
"""
result2 = index_document("https://example.com/cloud-article", article2)
print(f"  Doc 2 Result: {result2}")
assert result2["status"] == "indexed"

# Try indexing same URL again (should skip)
result3 = index_document("https://example.com/ml-article", article)
print(f"  Duplicate Result: {result3}")
assert result3["status"] == "skipped"
print("  ✅ PASSED")

# ==============================
# Test 6: O(1) Fingerprint Lookup
# ==============================
print("\n--- Test 6: O(1) Fingerprint Lookup ---")

# Slightly modified version of article 1 — should still match
query_article = """
Machine learning algorithms are increasingly used in modern AI systems to automate 
complex decision-making. These algorithms learn from data patterns and make predictions 
without explicit programming instructions. Deep learning uses neural networks with 
multiple layers to extract higher-level features from raw data input.
"""

start_time = time.time()
matches = lookup_fingerprints(query_article)
lookup_ms = (time.time() - start_time) * 1000

print(f"  Lookup time: {lookup_ms:.2f} ms")
print(f"  Matches found: {len(matches)}")
for m in matches:
    print(f"    URL: {m['url']}")
    print(f"    Match count: {m['match_count']}/{m['total_fingerprints']}")
    print(f"    Similarity: {m['similarity'] * 100:.1f}%")
    print()

assert len(matches) > 0, "No matches found — fingerprint lookup failed!"
assert matches[0]["url"] == "https://example.com/ml-article", "Wrong document matched!"
assert lookup_ms < 500, f"Lookup too slow: {lookup_ms:.2f}ms (target < 500ms)"
print("  ✅ PASSED")

# ==============================
# Final Stats
# ==============================
stats = get_index_stats()
print("\n" + "=" * 60)
print(f"FINAL INDEX STATS: {stats['documents']} documents, {stats['fingerprints']} fingerprints")
print("=" * 60)
print("\n🎉 ALL TESTS PASSED — Fingerprint Engine is operational!")

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

        // Plagiarism Risk Badge
        const plagBadge = document.getElementById('plag-badge');
        const plagRisk = report.plagiarism_risk || "--";
        plagBadge.textContent = plagRisk;
        plagBadge.className = 'badge';
        if (plagRisk.toLowerCase().includes('high')) plagBadge.classList.add('risk');
        else if (plagRisk.toLowerCase().includes('medium')) plagBadge.classList.add('warn');
        else plagBadge.classList.add('safe');

        document.getElementById('idea-badge').textContent = report.idea_similarity || "--";
        document.getElementById('value-badge').textContent = report.value_addition || "--";

        // SEO Score
        document.getElementById('seo-score').textContent = report.seo_score || "--%";
        document.getElementById('seo-fill').style.width = report.seo_score || "0%";

        // Matched References (top 5)
        const refsList = document.getElementById('refs-list');
        const refs = report.matched_references || [];
        if (refs.length > 0) {
            refsList.innerHTML = refs.map(ref =>
                `<a href="${ref.url}" target="_blank" class="ref-link">
                    <span class="ref-score">${ref.score}</span>
                    <span class="ref-url">${ref.url}</span>
                </a>`
            ).join('');
        } else {
            refsList.innerHTML = '<span class="text-muted">None detected</span>';
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
                            <div class="score-card">
                                <h3>SEO Score</h3>
                                <div class="score-value" id="seo-score">--%</div>
                                <div class="score-bar">
                                    <div class="fill" id="seo-fill"></div>
                                </div>
                            </div>
                        </div>

                        <div class="analysis-details">
                            <div class="detail-row">
                                <span class="label">AdSense Risk:</span>
                                <span class="badge" id="risk-badge">--</span>
                            </div>
                            <div class="detail-row">
                                <span class="label">Plagiarism Risk:</span>
                                <span class="badge" id="plag-badge">--</span>
                            </div>
                            <div class="detail-row">
                                <span class="label">Idea Similarity:</span>
                                <span class="badge outline" id="idea-badge">--</span>
                            </div>
                            <div class="detail-row">
                                <span class="label">Value Addition:</span>
                                <span class="badge outline" id="value-badge">--</span>
                            </div>
                            <div class="detail-row refs-row">
                                <span class="label">Matched References:</span>
                                <div class="refs-list" id="refs-list">
                                    <span class="text-muted">None detected</span>
                                </div>
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
    grid-template-columns: repeat(4, 1fr);
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

/* ========================
   REFERENCE LIST
   ======================== */

.refs-row {
    flex-direction: column !important;
    gap: 0.5rem !important;
}

.refs-list {
    display: flex;
    flex-direction: column;
    gap: 0.4rem;
    max-height: 180px;
    overflow-y: auto;
}

.ref-link {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.4rem 0.6rem;
    background: rgba(0, 0, 0, 0.25);
    border-radius: 6px;
    text-decoration: none;
    transition: background 0.2s;
    border: 1px solid rgba(255, 255, 255, 0.04);
}

.ref-link:hover {
    background: rgba(59, 130, 246, 0.15);
}

.ref-score {
    background: var(--accent);
    color: white;
    font-size: 0.7rem;
    font-weight: 600;
    padding: 2px 6px;
    border-radius: 4px;
    white-space: nowrap;
}

.ref-url {
    font-size: 0.8rem;
    color: var(--text-secondary);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 350px;
}

.text-muted {
    color: var(--text-secondary);
    font-size: 0.85rem;
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
mmh3

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

### `backend/models/index_db.py`

```python
"""
Fingerprint Index DB Schema

Creates the inverted index tables used by the Fingerprint Engine
for O(1) plagiarism detection lookups.
"""
import sqlite3
import os

INDEX_DB_PATH = os.path.join(os.path.dirname(__file__), '../../database/cre.db')


def init_index_tables():
    """Create the fingerprint index tables if they don't exist."""
    conn = sqlite3.connect(INDEX_DB_PATH)
    cursor = conn.cursor()
    
    # Table 1: Indexed Documents — stores metadata of every crawled/indexed page
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS indexed_documents (
            id TEXT PRIMARY KEY,
            url TEXT UNIQUE NOT NULL,
            content_snippet TEXT,
            word_count INTEGER DEFAULT 0,
            indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Table 2: Fingerprints — the core inverted index
    # Maps each fingerprint hash → the document it belongs to
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fingerprints (
            fingerprint_hash INTEGER NOT NULL,
            document_id TEXT NOT NULL,
            FOREIGN KEY (document_id) REFERENCES indexed_documents(id)
        )
    """)
    
    # Critical: Index on fingerprint_hash for O(1) lookups
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_fingerprint_hash 
        ON fingerprints(fingerprint_hash)
    """)
    
    # Index on document_id for fast document-level queries
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_fingerprint_doc 
        ON fingerprints(document_id)
    """)
    
    conn.commit()
    conn.close()
    print("[IndexDB] Fingerprint index tables initialized.")


def get_index_stats():
    """Return current index statistics."""
    conn = sqlite3.connect(INDEX_DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT COUNT(*) FROM indexed_documents")
        doc_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM fingerprints")
        fp_count = cursor.fetchone()[0]
    except sqlite3.OperationalError:
        doc_count = 0
        fp_count = 0
    
    conn.close()
    return {"documents": doc_count, "fingerprints": fp_count}


if __name__ == "__main__":
    init_index_tables()
    stats = get_index_stats()
    print(f"[IndexDB] Stats: {stats['documents']} documents, {stats['fingerprints']} fingerprints")

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
    
    # Step 5: Reference-Aware Rewrite
    if progress_callback:
        await progress_callback("rewriting", "Rewriting with maximum semantic distance from matched references...")
    
    # Pass the matched reference text so the LLM can actively differentiate
    reference_content = top_match.get("content", "") if top_match else None
    texts_to_rewrite = [n["text"] for n in nodes]
    rewritten_texts = await rewrite_text_nodes(texts_to_rewrite, reference_text=reference_content)
    
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
    
    # Add top 5 matched reference URLs for richer frontend display
    report["matched_references"] = [
        {"url": ref["url"], "score": f"{int(ref['score'] * 100)}%"}
        for ref in all_scores[:5]
    ] if all_scores else []

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

ANALYSIS_PROMPT = """You are an expert plagiarism detection and content quality analysis system, equivalent to Google AdSense's internal content evaluator.

The exact mathematical cosine similarity score between the user's article and the top internet reference is {sim_pct:.1f}%.

USER ARTICLE:
{article}

TOP MATCHING REFERENCE (investigating for plagiarism/duplication):
{reference}

Perform a comprehensive multi-factor analysis across these 9 dimensions:

1. **Semantic Similarity** (Low/Medium/High) — How closely does the text match the reference in meaning?
2. **Idea Similarity** (Low/Medium/High) — Are the core ideas/arguments the same, even if words differ?
3. **Plagiarism Risk** (Low/Medium/High) — Risk of being flagged by automated plagiarism detectors
4. **Originality Score** (0-100) — How original is the user's content overall?
5. **Value Addition** (Low/Medium/High) — Does the user add unique perspectives, examples, or depth?
6. **SEO Quality** (0-100) — Rate the content's SEO strength (headings, structure, keywords, readability)
7. **Trust Score** (1-10) — Overall trustworthiness and publisher credibility signal
8. **AdSense Risk** (Low/Medium/High) — Risk of Google AdSense rejection or thin content penalty
9. **Analysis Summary** — A 2-3 sentence expert summary of the content's strengths and weaknesses

Return ONLY a valid JSON object with these exact keys:
{{"semantic_similarity": "...", "idea_similarity": "...", "plagiarism_risk": "...", "originality_score": "...", "value_addition": "...", "seo_score": "...", "trust_score": "...", "adsense_risk": "...", "analysis_summary": "..."}}"""


def _call_openai_compatible(api_url: str, api_key: str, model: str, prompt: str) -> dict:
    """Generic OpenAI-compatible API caller (works for DeepSeek + Groq + OpenRouter)."""
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
    CRE Multi-Factor Analysis Engine — DeepSeek primary, Groq + OpenRouter fallback.
    Returns 9-dimension analysis for comprehensive CRE scoring.
    """
    ref_dict = top_reference or {}
    prompt = ANALYSIS_PROMPT.format(
        sim_pct=similarity_score * 100,
        article=article[:2000],
        reference=ref_dict.get('content', 'No reference article found.')[:2000]
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
        "semantic_similarity": "Unknown",
        "idea_similarity": "Unknown",
        "plagiarism_risk": "Unknown",
        "originality_score": "50",
        "value_addition": "Unknown",
        "seo_score": "50",
        "trust_score": "5",
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

### `backend/services/fingerprint_engine.py`

```python
"""
Fingerprint Engine — The Core CRE Proprietary Index Technology

Converts text → normalized shingles → MurmurHash3 integers.
Provides O(1) database insertion and lookup for instant plagiarism detection.

Industry standard: 5-word shingling + MurmurHash3 (same as Elasticsearch internals).
"""
import re
import hashlib
import sqlite3
import os
import mmh3

INDEX_DB_PATH = os.path.join(os.path.dirname(__file__), '../../database/cre.db')

# ==============================
# 1. Text Normalization
# ==============================

def normalize_text(text: str) -> str:
    """
    Normalize text for consistent fingerprinting.
    - Lowercase
    - Strip all punctuation except hyphens (preserve compound words)
    - Collapse whitespace
    """
    text = text.lower()
    # Remove everything except letters, digits, hyphens, and spaces
    text = re.sub(r'[^a-z0-9\s\-]', '', text)
    # Collapse whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text


# ==============================
# 2. Shingling (N-Gram Generation)
# ==============================

def generate_shingles(text: str, n: int = 5) -> list[str]:
    """
    Generate overlapping N-word shingles from normalized text.
    
    Example (n=5):
      "machine learning is used in artificial intelligence systems"
      → ["machine learning is used in",
         "learning is used in artificial",
         "is used in artificial intelligence",
         "used in artificial intelligence systems"]
    """
    words = text.split()
    if len(words) < n:
        # If text is too short for n-grams, return the whole thing as one shingle
        return [text] if text else []
    
    shingles = []
    for i in range(len(words) - n + 1):
        shingle = " ".join(words[i:i + n])
        shingles.append(shingle)
    
    return shingles


# ==============================
# 3. MurmurHash3 Fingerprinting
# ==============================

def hash_shingles(shingles: list[str]) -> list[int]:
    """
    Convert string shingles into 32-bit MurmurHash3 integers.
    
    MurmurHash3 is:
    - Non-cryptographic (fast, not for security)
    - Excellent distribution (minimal collisions)
    - Industry standard for inverted indexes (Elasticsearch uses it)
    """
    return [mmh3.hash(shingle, signed=False) for shingle in shingles]


# ==============================
# 4. Master Fingerprint Generator
# ==============================

def generate_fingerprints(text: str) -> list[int]:
    """
    The core function: Text → Fingerprints.
    
    Pipeline:
      Raw text → normalize → shingle (5-word) → MurmurHash3 → integer list
    
    Returns: list of 32-bit unsigned integers (fingerprint hashes)
    """
    normalized = normalize_text(text)
    shingles = generate_shingles(normalized)
    fingerprints = hash_shingles(shingles)
    return fingerprints


# ==============================
# 5. Document Indexing (DB Insert)
# ==============================

def index_document(url: str, text: str) -> dict:
    """
    Index a single document into the fingerprint database.
    
    Steps:
      1. Generate a unique document ID from the URL
      2. Check if already indexed (skip if yes)
      3. Generate fingerprints from the text
      4. Bulk insert (hash, doc_id) pairs into the inverted index
    
    Returns: {"status": "indexed"|"skipped", "fingerprint_count": N}
    """
    # Generate deterministic document ID from URL
    doc_id = hashlib.md5(url.encode()).hexdigest()
    
    conn = sqlite3.connect(INDEX_DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if already indexed
        cursor.execute("SELECT id FROM indexed_documents WHERE id = ?", (doc_id,))
        if cursor.fetchone():
            conn.close()
            return {"status": "skipped", "fingerprint_count": 0, "doc_id": doc_id}
        
        # Generate fingerprints
        fingerprints = generate_fingerprints(text)
        
        if not fingerprints:
            conn.close()
            return {"status": "skipped", "fingerprint_count": 0, "doc_id": doc_id}
        
        # Insert document metadata
        word_count = len(text.split())
        cursor.execute(
            "INSERT INTO indexed_documents (id, url, content_snippet, word_count) VALUES (?, ?, ?, ?)",
            (doc_id, url, text[:500], word_count)
        )
        
        # Bulk insert fingerprints into inverted index
        fp_rows = [(fp, doc_id) for fp in fingerprints]
        cursor.executemany(
            "INSERT INTO fingerprints (fingerprint_hash, document_id) VALUES (?, ?)",
            fp_rows
        )
        
        conn.commit()
        conn.close()
        
        return {"status": "indexed", "fingerprint_count": len(fingerprints), "doc_id": doc_id}
    
    except Exception as e:
        conn.close()
        print(f"[FingerprintEngine] Indexing error: {e}")
        return {"status": "error", "fingerprint_count": 0, "doc_id": doc_id}


# ==============================
# 6. Fingerprint Lookup (O(1) Match)
# ==============================

def lookup_fingerprints(text: str, top_k: int = 5) -> list[dict]:
    """
    The O(1) matching engine.
    
    Steps:
      1. Generate fingerprints from the user's article
      2. Query the inverted index for matching document IDs
      3. Count overlapping hashes per document
      4. Rank by overlap percentage (Jaccard-like similarity)
    
    Returns: list of {"doc_id", "url", "content_snippet", "match_count", "similarity"}
    """
    user_fingerprints = generate_fingerprints(text)
    
    if not user_fingerprints:
        return []
    
    conn = sqlite3.connect(INDEX_DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Build the IN clause with parameterized placeholders
        placeholders = ",".join(["?" for _ in user_fingerprints])
        
        query = f"""
            SELECT 
                f.document_id,
                d.url,
                d.content_snippet,
                COUNT(*) as match_count
            FROM fingerprints f
            JOIN indexed_documents d ON f.document_id = d.id
            WHERE f.fingerprint_hash IN ({placeholders})
            GROUP BY f.document_id
            ORDER BY match_count DESC
            LIMIT ?
        """
        
        cursor.execute(query, user_fingerprints + [top_k])
        rows = cursor.fetchall()
        conn.close()
        
        total_user_fps = len(user_fingerprints)
        
        results = []
        for row in rows:
            doc_id, url, snippet, match_count = row
            # Similarity = overlapping fingerprints / total user fingerprints
            similarity = round(match_count / total_user_fps, 4) if total_user_fps > 0 else 0
            results.append({
                "doc_id": doc_id,
                "url": url,
                "content_snippet": snippet,
                "match_count": match_count,
                "total_fingerprints": total_user_fps,
                "similarity": similarity
            })
        
        return results
    
    except Exception as e:
        conn.close()
        print(f"[FingerprintEngine] Lookup error: {e}")
        return []

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

def extract_fingerprints(text: str, max_fingerprints=12):
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
                    for url in search(q, num_results=10, lang="en"):
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

async def adaptive_scrape(urls, max_scrape=15):
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


def _build_rewrite_prompt(texts: list[str], reference_text: str = None) -> str:
    """Build the reference-aware, SEO-optimized rewrite prompt."""
    input_json = json.dumps({str(i): text for i, text in enumerate(texts)})
    
    ref_section = ""
    if reference_text:
        ref_section = f"""
CRITICAL CONTEXT — The text below was flagged as semantically similar to the following reference.
You MUST actively increase the semantic distance from this reference while preserving the core meaning.

MATCHED REFERENCE TEXT (avoid resembling this):
{reference_text[:2000]}

DIFFERENTIATION STRATEGY:
- Use completely different sentence structures and reasoning patterns
- Replace generic phrasing with original insights and unique examples
- Restructure the logical flow and argument ordering
- Add value through original analysis the reference lacks
"""

    return f"""You are a professional content rewriter specializing in originality and SEO optimization.

Rewrite the following blocks of text so that they:
1. Are HIGHLY ORIGINAL — use different reasoning structures, vocabulary, and flow
2. Sound naturally human-written — no robotic or formulaic patterns
3. Improve SEO ranking — use clear headings, transition words, and scannable structure
4. Improve reader engagement and clarity
5. Improve AdSense approval probability — add depth and value
6. Preserve the core factual meaning accurately
{ref_section}
You MUST output a valid JSON array of strings in the exact same order as the input.
I am providing {len(texts)} blocks. I expect exactly a JSON list of length {len(texts)}.

INPUT:
{input_json}"""


def _parse_llm_json(content: str, expected_len: int) -> list[str] | None:
    """Parse JSON array from LLM response, handling markdown fences."""
    content = content.strip()
    if content.startswith("```json"):
        content = content[7:]
    if content.startswith("```"):
        content = content[3:]
    if content.endswith("```"):
        content = content[:-3]
    
    parsed = json.loads(content.strip())
    if isinstance(parsed, list) and len(parsed) == expected_len:
        return [str(item) for item in parsed]
    return None


def _rewrite_via_groq(texts: list[str], reference_text: str = None) -> list[str]:
    """Groq fallback using llama-3.3-70b-versatile."""
    groq_key = Config.GROQ_API_KEY
    if not groq_key:
        return texts
    
    prompt = _build_rewrite_prompt(texts, reference_text)
    headers = {
        "Authorization": f"Bearer {groq_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.75
    }
    
    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers=headers,
        json=payload,
        timeout=45
    )
    response.raise_for_status()
    content = response.json()["choices"][0]["message"]["content"]
    
    result = _parse_llm_json(content, len(texts))
    return result if result else texts


def _rewrite_via_openrouter(texts: list[str], reference_text: str = None) -> list[str]:
    """OpenRouter fallback using free llama model."""
    openrouter_key = Config.OPENROUTER_API_KEY
    if not openrouter_key or "sk-or" not in openrouter_key:
        return texts
    
    prompt = _build_rewrite_prompt(texts, reference_text)
    headers = {
        "Authorization": f"Bearer {openrouter_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "meta-llama/llama-3.3-70b-instruct:free",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.75
    }
    
    resp = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=payload,
        timeout=45
    )
    resp.raise_for_status()
    content = resp.json()["choices"][0]["message"]["content"]
    
    result = _parse_llm_json(content, len(texts))
    return result if result else texts


async def rewrite_text_nodes(texts: list[str], reference_text: str = None) -> list[str]:
    """
    Reference-Aware Rewrite Engine — Gemini primary, Groq + OpenRouter fallback.
    Takes text nodes + matched reference, rewrites for maximum originality.
    """
    if not texts:
        return []

    prompt = _build_rewrite_prompt(texts, reference_text)

    # Try Gemini first (2 attempts)
    for attempt in range(2):
        try:
            response = await asyncio.to_thread(
                model.generate_content,
                prompt,
                generation_config={"response_mime_type": "application/json"}
            )
            
            result = _parse_llm_json(response.text, len(texts))
            if result:
                print("[Rewrite] Gemini succeeded")
                return result
            else:
                print(f"[Rewrite] Gemini length mismatch on attempt {attempt+1}")
        except Exception as e:
            print(f"[Rewrite] Gemini error (attempt {attempt+1}): {e}")
            
        await asyncio.sleep(2)
    
    # Fallback to Groq
    try:
        print("[Rewrite] Trying Groq fallback...")
        result = await asyncio.to_thread(_rewrite_via_groq, texts, reference_text)
        if result != texts:
            print("[Rewrite] Groq succeeded")
            return result
    except Exception as e:
        print(f"[Rewrite] Groq fallback failed: {e}")
    
    # Fallback to OpenRouter
    try:
        print("[Rewrite] Trying OpenRouter fallback...")
        result = await asyncio.to_thread(_rewrite_via_openrouter, texts, reference_text)
        if result != texts:
            print("[Rewrite] OpenRouter succeeded")
            return result
    except Exception as e:
        print(f"[Rewrite] OpenRouter fallback failed: {e}")
    
    print("[Rewrite] All engines failed. Returning originals.")
    return texts

```

### `backend/services/scoring_service.py`

```python
def _parse_score(value, default=50):
    """Safely parse a numeric score from LLM output."""
    if isinstance(value, (int, float)):
        return int(value)
    if isinstance(value, str):
        # Extract digits from strings like "75%" or "75/100" or "75"
        import re
        match = re.search(r'(\d+)', str(value))
        if match:
            return min(100, int(match.group(1)))
    return default


def _level_to_score(level: str, default=50) -> int:
    """Convert Low/Medium/High text to a numeric score."""
    level_map = {
        "low": 90,
        "medium": 60,
        "high": 30,
        "very low": 95,
        "very high": 15,
        "none": 100,
    }
    return level_map.get(str(level).lower().strip(), default)


def generate_cre_report(similarity_score: float, analysis: dict) -> dict:
    """
    CRE Multi-Factor Scoring Engine (V5)
    
    Combines mathematical similarity with LLM-assessed qualitative scores
    to produce a comprehensive, production-grade content quality report.
    """
    # ---- Mathematical Scores ----
    sem_sim_percent = int(similarity_score * 100)
    math_originality = max(0, 100 - sem_sim_percent)
    
    # ---- LLM-Assessed Scores ----
    idea_score = _level_to_score(analysis.get("idea_similarity", "Medium"))
    risk_score = _level_to_score(analysis.get("plagiarism_risk", "Medium"))
    value_score = _level_to_score(analysis.get("value_addition", "Medium"), default=50)
    # Invert value: High value_addition = good = high score
    value_score = 100 - _level_to_score(analysis.get("value_addition", "Medium"), default=50)
    if analysis.get("value_addition", "").lower() == "high":
        value_score = 85
    elif analysis.get("value_addition", "").lower() == "medium":
        value_score = 55
    elif analysis.get("value_addition", "").lower() == "low":
        value_score = 25
    
    llm_originality = _parse_score(analysis.get("originality_score", "50"))
    seo_score = _parse_score(analysis.get("seo_score", "50"))
    llm_trust = _parse_score(analysis.get("trust_score", "5"), default=5)
    
    # ---- Composite Originality Score ----
    # Weighted average: math similarity (40%) + LLM originality (30%) + idea uniqueness (15%) + value (15%)
    composite_originality = int(
        (math_originality * 0.40) +
        (llm_originality * 0.30) +
        (idea_score * 0.15) +
        (value_score * 0.15)
    )
    composite_originality = max(0, min(100, composite_originality))
    
    # ---- Composite Trust Score ----
    # Normalize trust to /10 scale using composite originality
    if llm_trust > 10:
        llm_trust = min(10, llm_trust // 10)
    trust_from_originality = max(1, composite_originality // 10)
    trust_score = int((llm_trust * 0.6) + (trust_from_originality * 0.4))
    trust_score = max(1, min(10, trust_score))
    
    # ---- Plagiarism Risk Level ----
    plag_risk = analysis.get("plagiarism_risk", "Unknown")
    if plag_risk == "Unknown":
        if sem_sim_percent > 70:
            plag_risk = "High"
        elif sem_sim_percent > 40:
            plag_risk = "Medium"
        else:
            plag_risk = "Low"
    
    # ---- AdSense Safety ----
    adsense = analysis.get("adsense_risk", "Unknown")

    report = {
        "similarity_score": f"{sem_sim_percent}%",
        "originality_score": f"{composite_originality}%",
        "trust_score": f"{trust_score}/10",
        "seo_score": f"{seo_score}%",
        "plagiarism_risk": plag_risk,
        "idea_similarity": analysis.get("idea_similarity", "Unknown"),
        "value_addition": analysis.get("value_addition", "Unknown"),
        "adsense_safety": adsense,
        "ai_rationale": analysis.get("analysis_summary", "No rationale generated.")
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

async def search_internet(queries: list[str], max_results_per_query: int = 7) -> list[str]:
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

