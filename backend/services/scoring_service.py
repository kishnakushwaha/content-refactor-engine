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
