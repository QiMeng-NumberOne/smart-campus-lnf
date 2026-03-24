"""
Configuration for the Recommendation System Engine.
"""

import os

# Text/Image Semantic Extraction Model
# Redirected to local model folder within the repository
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_NAME = os.path.join(BASE_DIR, "pretrained_model")

# Five-dimensional Fusion Weights
WEIGHT_IMAGE = 0.40
WEIGHT_TEXT = 0.30
WEIGHT_LOCATION = 0.20
WEIGHT_TIME = 0.10
WEIGHT_COLLABORATIVE = 0.00  # Initial placeholder for future user behavior feedback
