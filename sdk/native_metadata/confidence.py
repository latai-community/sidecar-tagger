"""
Title: Confidence Calculator
Abstract: Calculates confidence score based on available native metadata.
Why: Determines if Layer 1 alone is sufficient or needs Layers 2-3.
"""
from typing import Dict, Any

CONFIDENCE_THRESHOLD = 0.8


def calculate_confidence(metadata: Dict[str, Any]) -> float:
    """
    Calculate confidence score 0.0 - 1.0 based on available metadata.
    
    Higher confidence = more metadata available from native sources
    (author, title, keywords, etc.) without needing AI.
    
    Args:
        metadata: Mapped native metadata
        
    Returns:
        Confidence score between 0.0 and 1.0
    """
    score = 0.0
    
    if not metadata:
        return 0.0
    
    high_priority = ["author", "title"]
    medium_priority = ["keywords", "subject"]
    low_priority = ["date", "create_date", "camera_make", "camera_model"]
    
    for key in high_priority:
        if metadata.get(key):
            if key in ["author", "title"] and metadata.get("author") and metadata.get("title"):
                score += 0.5
                break
            elif metadata.get(key):
                score += 0.25
                break
    
    for key in medium_priority:
        if metadata.get(key):
            score += 0.2
            break
    
    for key in low_priority:
        if metadata.get(key):
            score += 0.1
            break
    
    if metadata.get("gps_lat") and metadata.get("gps_lon"):
        score += 0.1
    
    return min(score, 1.0)


def should_shortcut(confidence: float, threshold: float = CONFIDENCE_THRESHOLD) -> bool:
    """
    Determine if we should shortcut to Layer 1 only.
    
    Args:
        confidence: Calculated confidence score
        threshold: Threshold to trigger shortcut (default: 0.8)
        
    Returns:
        True if confidence >= threshold
    """
    return confidence >= threshold


def get_confidence_level(confidence: float) -> str:
    """
    Get human-readable confidence level.
    
    Args:
        confidence: Confidence score
        
    Returns:
        Level description
    """
    if confidence >= 0.8:
        return "high"
    elif confidence >= 0.5:
        return "medium"
    elif confidence >= 0.25:
        return "low"
    return "minimal"


if __name__ == "__main__":
    test_cases = [
        {"author": "John", "title": "Test Doc"},
        {"author": "Jane"},
        {"keywords": "test,docs"},
        {"date": "2024-01-01"},
        {"camera_make": "Canon", "camera_model": "EOS"},
        {},
    ]
    
    for metadata in test_cases:
        confidence = calculate_confidence(metadata)
        shortcut = should_shortcut(confidence)
        level = get_confidence_level(confidence)
        print(f"Metadata: {metadata}")
        print(f"  Confidence: {confidence:.2f} ({level})")
        print(f"  Shortcut: {shortcut}")
        print()
