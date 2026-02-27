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
