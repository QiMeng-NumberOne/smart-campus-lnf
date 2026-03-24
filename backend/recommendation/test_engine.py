from datetime import datetime, timedelta
from .ranker import recommendation_engine

def run_tests():
    print("--- Starting Recommendation Engine Logic Tests ---")
    
    now = datetime.now()
    # Dummy Target: Looking for a blue umbrella
    target = {
        "id": "Lost_1",
        "image_path": None, # Skipping image comparison to avoid downloading large models during logic test
        "text_desc": "Blue umbrella",
        "lat": 39.90,
        "lon": 116.40,
        "time_iso": now.isoformat()
    }

    # Perfect Match
    candidate_1 = {
        "id": "Found_1",
        "image_path": None,
        "text_desc": "Blue umbrella",
        "lat": 39.90,
        "lon": 116.40,
        "time_iso": now.isoformat()
    }

    # Bad Match (Far away, old)
    candidate_2 = {
        "id": "Found_2",
        "image_path": None,
        "text_desc": "Blue umbrella",
        "lat": 40.00,
        "lon": 116.50,
        "time_iso": (now - timedelta(days=20)).isoformat()
    }

    results = recommendation_engine.get_top_k_recommendations(target, [candidate_1, candidate_2], top_k=2)
    
    for r in results:
        print(f"Candidate {r['item']['id']} score: {r['score']}")
        
    assert results[0]["item"]["id"] == "Found_1", "Found_1 should be the top match."
    print("Tests passed successfully!")

if __name__ == "__main__":
    run_tests()
