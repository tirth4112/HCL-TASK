import json
from sqlalchemy import text
from .database import DatabaseManager, PolicyRule
from .embeddings import EmbeddingProvider

class PolicyRepository:
    def __init__(self, db_manager: DatabaseManager, embedding_provider: EmbeddingProvider):
        self.db = db_manager
        self.embeddings = embedding_provider

    def ingest_policy_rules(self, json_path: str) -> int:
        with open(json_path, 'r') as f:
            policies = json.load(f)
        
        session = self.db.get_session()
        count = 0
        try:
            for p in policies:
                # Check if exists
                existing = session.query(PolicyRule).filter_by(policy_id=p['policy_id']).first()
                if not existing:
                    vector = self.embeddings.embed_text(p['policy_text'])
                    new_rule = PolicyRule(
                        policy_id=p['policy_id'],
                        title=p['title'],
                        category=p['category'],
                        policy_text=p['policy_text'],
                        embedding=vector
                    )
                    session.add(new_rule)
                    count += 1
            session.commit()
            return count
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def search_policy(self, query: str, top_k: int = 5) -> list[dict]:
        query_embedding = self.embeddings.embed_text(query)
        session = self.db.get_session()
        try:
            # Local cosine similarity calculation instead of pgvector
            import math
            def cosine_sim(vec1, vec2):
                if not vec1 or not vec2: return 0.0
                dot = sum(a*b for a, b in zip(vec1, vec2))
                norm1 = math.sqrt(sum(a*a for a in vec1))
                norm2 = math.sqrt(sum(b*b for b in vec2))
                return dot / (norm1 * norm2) if norm1 and norm2 else 0.0
                
            all_policies = session.query(PolicyRule).all()
            
            results = []
            for r in all_policies:
                sim = cosine_sim(r.embedding, query_embedding)
                results.append({
                    "policy_id": r.policy_id,
                    "title": r.title,
                    "policy_text": r.policy_text,
                    "similarity": sim
                })
            
            # Sort by similarity descending
            results.sort(key=lambda x: x['similarity'], reverse=True)
            return results[:top_k]
        finally:
            session.close()