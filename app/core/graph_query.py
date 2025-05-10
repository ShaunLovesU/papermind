from typing import List, Tuple
from neo4j import GraphDatabase
from app.core.config import settings
from app.utils.embedding_utils import get_text_embedding, cosine_similarity
from multiprocessing import Pool, cpu_count

def score_entity_worker(args):
    name, embedding, query_vector = args
    from app.utils.embedding_utils import cosine_similarity  # 避免循环引用
    score = cosine_similarity(query_vector, embedding)
    return (name, score)

class GraphQueryWithEmbedding:
    def __init__(self, uri: str, user: str, password: str):
        try:
            self.driver = GraphDatabase.driver(uri, auth=(user, password))
            with self.driver.session() as session:
                session.run("RETURN 1")
            print("Connected to Neo4j.")
        except Exception as e:
            print(f"Failed to connect to Neo4j: {e}")
            raise

    def close(self):
        self.driver.close()

    def get_all_entities_with_embeddings(self) -> List[Tuple[str, List[float]]]:
        try:
            query = """
            MATCH (e:Entity)
            WHERE e.embedding IS NOT NULL
            RETURN e.name AS name, e.embedding AS embedding
            """
            with self.driver.session() as session:
                result = session.execute_read(lambda tx: tx.run(query).data())

            return [(row["name"], row["embedding"]) for row in result if row["embedding"]]
        except Exception as e:
            print(f"Failed to fetch entities with embeddings: {e}")
            return []

    def find_top_k_entities(self, query_vector: List[float], top_k: int = 3, processes: int = 4) -> List[str]:
        try:
            all_entities = self.get_all_entities_with_embeddings()
            if not all_entities:
                return []
            args_list = [(name, emb, query_vector) for name, emb in all_entities]
            with Pool(processes=processes) as pool:
                scored = pool.map(score_entity_worker, args_list)

            scored.sort(key=lambda x: x[1], reverse=True)
            return [name for name, _ in scored[:top_k]]
        except Exception as e:
            print(f"Failed to compute top-k similar entities: {e}")
            return []

    def get_triplets_by_entities(self, entity_names: List[str]) -> List[Tuple[str, str, str]]:
        try:
            query = """
            MATCH (h:Entity)-[r]->(t:Entity)
            WHERE h.name IN $names OR t.name IN $names
            RETURN h.name, type(r), t.name
            """
            with self.driver.session() as session:
                result = session.execute_read(lambda tx: tx.run(query, names=entity_names).data())

            return [(row["h.name"], row["type(r)"], row["t.name"]) for row in result]
        except Exception as e:
            print(f"Failed to fetch triplets: {e}")
            return []


if __name__ == "__main__":
    try:
        query_client = GraphQueryWithEmbedding(
            settings.NEO4J_URI,
            settings.NEO4J_USER,
            settings.NEO4J_PASSWORD
        )

        user_query = input("Enter your query: ")
        query_vec = get_text_embedding(user_query)

        if not query_vec:
            print("Failed to get embedding for query.")
        else:
            top_entities = query_client.find_top_k_entities(query_vec, top_k=3, processes=4)
            print(f"Top matched entities: {top_entities}")

            triplets = query_client.get_triplets_by_entities(top_entities)
            if not triplets:
                print("No related triplets found.")
            else:
                print(f"Found {len(triplets)} triplets:")
                for h, r, t in triplets:
                    print(f"({h}) -[{r}]-> ({t})")

        query_client.close()

    except Exception as e:
        print(f"Query system failed: {e}")
