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
