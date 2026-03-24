from typing import List, Dict, Any
from .config import WEIGHT_IMAGE, WEIGHT_TEXT, WEIGHT_LOCATION, WEIGHT_TIME, WEIGHT_COLLABORATIVE
from .clip_engine import clip_engine
from .scoring_utils import calc_location_score, calc_time_score

class RecommendationEngine:
    def __init__(self):
        pass

    def _calculate_comprehensive_score(self, target: Dict[str, Any], candidate: Dict[str, Any]) -> float:
        """
        Calculate the 5-dimensional weighted score between target and candidate.
        Expected target/candidate dict format:
        {
            "id": 1,
            "image_path": "path/to/img.jpg",
            "text_desc": "blue umbrella",
            "lat": 39.9,
            "lon": 116.4,
            "time_iso": "2026-03-23T10:00:00",
            "collab_score": 0.0 # Placeholder
        }
        """
        # 1. Image Similarity
        img_score = 0.0
        if target.get("image_path") and candidate.get("image_path"):
            feat1 = clip_engine.get_image_feature(target["image_path"])
            feat2 = clip_engine.get_image_feature(candidate["image_path"])
            img_score = clip_engine.cosine_similarity(feat1, feat2)

        # 2. Text Similarity
        text_score = 0.0
        if target.get("text_desc") and candidate.get("text_desc"):
            feat1 = clip_engine.get_text_feature(target["text_desc"])
            feat2 = clip_engine.get_text_feature(candidate["text_desc"])
            text_score = clip_engine.cosine_similarity(feat1, feat2)

        # 3. Location Similarity
        loc_score = calc_location_score(
            target.get("lat"), target.get("lon"),
            candidate.get("lat"), candidate.get("lon")
        )

        # 4. Time Similarity
        time_score = calc_time_score(
            target.get("time_iso"), candidate.get("time_iso")
        )

        # 5. Collaborative Filtering Score (Placeholder for user behavior)
        collab_score = candidate.get("collab_score", 0.0)

        # Calculate weighted sum
        total_score = (
            WEIGHT_IMAGE * img_score +
            WEIGHT_TEXT * text_score +
            WEIGHT_LOCATION * loc_score +
            WEIGHT_TIME * time_score +
            WEIGHT_COLLABORATIVE * collab_score
        )
        return total_score

    def get_top_k_recommendations(self, target_item: Dict[str, Any], candidates: List[Dict[str, Any]], top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Rank candidates against the target item and return top-k results.
        Returns a sorted list of dicts: {"item": candidate, "score": score}
        """
        scored_candidates = []
        for candidate in candidates:
            score = self._calculate_comprehensive_score(target_item, candidate)
            scored_candidates.append({
                "item": candidate,
                "score": round(score, 4)
            })

        # Sort descending
        scored_candidates.sort(key=lambda x: x["score"], reverse=True)

        return scored_candidates[:top_k]

recommendation_engine = RecommendationEngine()
