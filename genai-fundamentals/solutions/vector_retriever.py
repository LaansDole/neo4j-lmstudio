import os

from dotenv import load_dotenv

load_dotenv()

# end::import-retriever[]
from lmstudio_client import get_embedding_model, get_lmstudio_embedding
from neo4j import GraphDatabase

# tag::import-embedder[]
from neo4j_graphrag.embeddings import Embedder

# end::import-embedder[]
# tag::import-retriever[]
from neo4j_graphrag.retrievers import VectorRetriever

# Connect to Neo4j database
driver = GraphDatabase.driver(os.getenv("NEO4J_URI"), auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD")))


# Create custom embedder for LM Studio
class LMStudioEmbedder(Embedder):
    def __init__(self, model_name=None):
        self.model = get_lmstudio_embedding(model_name)

    def embed_query(self, text: str):
        result = self.model.embed(text)
        return result.data

    def embed_documents(self, texts):
        embeddings = []
        for text in texts:
            result = self.model.embed(text)
            embeddings.append(result.data)
        return embeddings


# tag::embedder[]
# Create embedder with LM Studio
embedder = LMStudioEmbedder(get_embedding_model())
# end::embedder[]

# tag::retriever[]
# Create retriever
retriever = VectorRetriever(
    driver,
    index_name="moviePlots",
    embedder=embedder,
    return_properties=["title", "plot"],
)
# end::retriever[]

# tag::search[]
# Search for similar items
result = retriever.search(query_text="Toys coming alive", top_k=5)
# end::search[]

# tag::print-results[]
# Parse results
for item in result.items:
    print(item.content, item.metadata["score"])
# end::print-results[]

# Close the database connection
driver.close()
