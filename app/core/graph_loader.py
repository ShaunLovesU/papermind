from typing import List, Tuple
from neo4j import GraphDatabase
from app.core.config import settings  # ✅ 使用统一的 config

class GraphLoader:
    def __init__(self, uri: str, user: str, password: str):
        """
        Initialize the Neo4j driver.
        """
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        """
        Close the Neo4j driver connection.
        """
        self.driver.close()

    def load_triplets(self, triplets: List[Tuple[str, str, str]]):
        """
        Load a list of triplets into the Neo4j graph database.
        """
        with self.driver.session() as session:
            for head, relation, tail in triplets:
                session.execute_write(self._create_relationship, head, relation, tail)

    @staticmethod
    def _create_relationship(tx, head: str, relation: str, tail: str):
        """
        Create nodes and relationship in Neo4j. Avoid duplication using MERGE.
        """
        query = """
        MERGE (h:Entity {name: $head})
        MERGE (t:Entity {name: $tail})
        MERGE (h)-[r:%s]->(t)
        """ % relation.replace(" ", "_").upper()

        tx.run(query, head=head, tail=tail)

# if __name__ == "__main__":
#     # Example test triplets
#     triplets = [
#         ("Transformer", "was proposed by", "Vaswani et al."),
#         ("Transformer", "is based on", "Self-attention mechanism"),
#         ("Our model", "uses", "Positional encoding"),
#     ]
#
#     # Initialize graph loader using config settings
#     loader = GraphLoader(settings.NEO4J_URI, settings.NEO4J_USER, settings.NEO4J_PASSWORD)
#
#     # Load triplets into the graph
#     loader.load_triplets(triplets)
#     loader.close()
#
#     print("✅ Triplets have been loaded into Neo4j.")