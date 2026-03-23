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
