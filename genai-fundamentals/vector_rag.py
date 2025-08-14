import os

from dotenv import load_dotenv

load_dotenv()

from lmstudio_client import get_chat_model, get_embedding_model, get_lmstudio_embedding, get_lmstudio_llm
from neo4j import GraphDatabase
from neo4j_graphrag.embeddings import Embedder
from neo4j_graphrag.generation import GraphRAG
from neo4j_graphrag.llm import LLMInterface
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


# Create custom LLM interface for LM Studio
class LMStudioLLM(LLMInterface):
    def __init__(self, model_name=None):
        self.model = get_lmstudio_llm(model_name)

    def invoke(self, input: str) -> str:
        response = self.model.respond(input)
        return response


# Create embedder with LM Studio
embedder = LMStudioEmbedder(get_embedding_model())

# Create retriever
retriever = VectorRetriever(
    driver,
    index_name="moviePlots",
    embedder=embedder,
    return_properties=["title", "plot"],
)

# Create the LLM with LM Studio
llm = LMStudioLLM(get_chat_model())

# Create GraphRAG pipeline
rag = GraphRAG(retriever=retriever, llm=llm)

# Search
query_text = "Find me movies about toys coming alive"

response = rag.search(query_text=query_text, retriever_config={"top_k": 5}, return_context=True)

print(response.answer)
print("CONTEXT:", response.retriever_result.items)

# Close the database connection
driver.close()
