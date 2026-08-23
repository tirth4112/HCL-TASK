from sentence_transformers import SentenceTransformer

class EmbeddingProvider:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
    
    def embed_text(self, text: str) -> list[float]:
        return self.model.encode(text).tolist()
    
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self.model.encode(texts).tolist()
