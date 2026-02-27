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
