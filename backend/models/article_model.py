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
