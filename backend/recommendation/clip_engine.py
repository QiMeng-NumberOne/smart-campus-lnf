try:
    import torch
    from transformers import ChineseCLIPProcessor, ChineseCLIPModel
    from PIL import Image
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    print("[MOCK MODE] Warning: transformers/torch not installed. CLIPEngine will return deterministic mock vectors.")

from .config import MODEL_NAME
import os

class CLIPEngine:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CLIPEngine, cls).__new__(cls)
            cls._instance.device = "cuda" if torch.cuda.is_available() else "cpu"
            cls._instance.model = None
            cls._instance.processor = None
            cls._instance._load_model()
        return cls._instance

    def _load_model(self):
        """Lazy load the model to save memory if not immediately needed"""
        if not AI_AVAILABLE:
            self.model = "MOCK"
            return
            
        print(f"Loading Chinese-CLIP model ({MODEL_NAME}) on {self.device}...")
        try:
            # os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com' # Use mirror if needed in China
            self.model = ChineseCLIPModel.from_pretrained(MODEL_NAME).to(self.device)
            self.processor = ChineseCLIPProcessor.from_pretrained(MODEL_NAME)
            self.model.eval()
            print("Chinese-CLIP model loaded successfully.")
        except Exception as e:
            print(f"Warning: Failed to load Chinese-CLIP model: {e}")
            self.model = None
            self.processor = None

    def get_image_feature(self, image_path: str):
        """Extract image feature vector"""
        if not AI_AVAILABLE: return "mock_image_feature"
        
        if not self.model or not os.path.exists(image_path): 
            return None
        try:
            image = Image.open(image_path).convert("RGB")
            inputs = self.processor(images=image, return_tensors="pt").to(self.device)
            with torch.no_grad():
                outputs = self.model.get_image_features(**inputs)
                if isinstance(outputs, torch.Tensor):
                    image_features = outputs
                elif hasattr(outputs, "image_embeds"):
                    image_features = outputs.image_embeds
                elif hasattr(outputs, "pooler_output"):
                    image_features = outputs.pooler_output
                else:
                    image_features = outputs[0][:, 0, :] # fallback to CLS
                # Normalize
                image_features = image_features / image_features.norm(p=2, dim=-1, keepdim=True)
            return image_features
        except Exception as e:
            print(f"Error extracting image feature: {e}")
            return None

    def get_text_feature(self, text: str):
        """Extract text feature vector"""
        if not AI_AVAILABLE: return str(text).strip()
        
        if not self.model or not text.strip(): 
            return None
        try:
            inputs = self.processor(text=[text], return_tensors="pt", padding=True).to(self.device)
            with torch.no_grad():
                outputs = self.model.get_text_features(**inputs)
                if isinstance(outputs, torch.Tensor):
                    text_features = outputs
                elif hasattr(outputs, "text_embeds"):
                    text_features = outputs.text_embeds
                elif hasattr(outputs, "pooler_output"):
                    text_features = outputs.pooler_output
                else:
                    text_features = outputs[0][:, 0, :] # fallback to CLS
                # Normalize
                text_features = text_features / text_features.norm(p=2, dim=-1, keepdim=True)
            return text_features
        except Exception as e:
            print(f"Error extracting text feature: {e}")
            return None

    def cosine_similarity(self, vec1, vec2) -> float:
        """Calculate cosine similarity between two normalized vectors, returning [0, 1]"""
        if not AI_AVAILABLE:
            if vec1 == vec2: return 1.0
            return 0.3 # completely mock similarity if not identical
            
        if vec1 is None or vec2 is None:
            return 0.0
        # Given they are normalized, dot product gives cosine similarity [-1, 1]
        similarity = (vec1 @ vec2.T).squeeze().item()
        
        # We clamp it to [0, 1] to avoid negative score penalties in weighting
        return max(0.0, min(1.0, similarity))

# Expose a singleton
clip_engine = CLIPEngine()
