from typing import List, Tuple
from neo4j import GraphDatabase
from app.core.config import settings
from app.utils.embedding_utils import batch_get_embeddings


class GraphLoaderWithEmbedding:
    def __init__(self, uri: str, user: str, password: str):
        try:
            self.driver = GraphDatabase.driver(uri, auth=(user, password))
            # 测试连接
            with self.driver.session() as session:
                session.run("RETURN 1")
            print("Connected to Neo4j.")
        except Exception as e:
            print(f"Failed to connect to Neo4j: {e}")
            raise

    def close(self):
        self.driver.close()

    def load_triplets_with_embeddings(self, triplets: List[Tuple[str, str, str]]):
        try:
            # Step 1: Collect all unique entity names
            entity_set = set()
            for h, _, t in triplets:
                entity_set.add(h)
                entity_set.add(t)
            entity_list = list(entity_set)

            print(f"Generating embeddings for {len(entity_list)} entities...")
            embeddings = batch_get_embeddings(entity_list, processes=4)

            print(f"Writing triplets and embeddings into Neo4j...")
            with self.driver.session() as session:
                for h, r, t in triplets:
                    h_emb = embeddings.get(h, [])
                    t_emb = embeddings.get(t, [])
                    try:
                        session.execute_write(self._merge_triplet_with_embedding, h, r, t, h_emb, t_emb)
                    except Exception as e:
                        print(f"Failed to write triplet ({h}, {r}, {t}): {e}")

            print("All triplets and embeddings loaded.")
        except Exception as e:
            print(f"Unexpected error during embedding or writing: {e}")

    @staticmethod
    def _merge_triplet_with_embedding(tx, head, relation, tail, head_emb, tail_emb):
        query = """
        MERGE (h:Entity {name: $head})
        SET h.embedding = $head_emb
        MERGE (t:Entity {name: $tail})
        SET t.embedding = $tail_emb
        MERGE (h)-[r:%s]->(t)
        """ % relation.replace(" ", "_").upper()

        tx.run(query, head=head, tail=tail, head_emb=head_emb, tail_emb=tail_emb)


if __name__ == "__main__":
    try:
        triplets = [
            ("Transformer", "was proposed by", "Vaswani et al."),
            ("Transformer", "is based on", "Self-attention mechanism"),
            ("Our model", "uses", "Positional encoding"),
        ]

        loader = GraphLoaderWithEmbedding(
            settings.NEO4J_URI,
            settings.NEO4J_USER,
            settings.NEO4J_PASSWORD
        )

        loader.load_triplets_with_embeddings(triplets)
        loader.close()

    except Exception as e:
        print(f"💥 Loader failed: {e}")
