import os

from dotenv import load_dotenv

load_dotenv()

# end::import-graphrag[]
from lmstudio_client import client, get_chat_model, get_embedding_model, get_lmstudio_embedding, get_lmstudio_llm
from neo4j import GraphDatabase
from neo4j_graphrag.embeddings import Embedder

# end::import-llm[]
# tag::import-graphrag[]
from neo4j_graphrag.generation import GraphRAG

# tag::import-llm[]
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
        messages = [{"role": "user", "content": input}]
        response = client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
        )
        return response.choices[0].message.content


# Create embedder with LM Studio
embedder = LMStudioEmbedder(get_embedding_model())

# Create retriever
retriever = VectorRetriever(
    driver,
    index_name="moviePlots",
    embedder=embedder,
    return_properties=["title", "plot"],
)

# tag::llm[]
# Create the LLM with LM Studio
llm = LMStudioLLM(get_chat_model())
# end::llm[]

# tag::llm-temp[]
# Modify the LLM configuration if needed
llm = LMStudioLLM(get_chat_model())
# end::llm-temp[]

# tag::graphrag[]
# Create GraphRAG pipeline
rag = GraphRAG(retriever=retriever, llm=llm)
# end::graphrag[]

# tag::search[]
# Search
query_text = "Find me movies about toys coming alive"

response = rag.search(query_text=query_text, retriever_config={"top_k": 5})

print(response.answer)
# end::search[]

# tag::search_return_context[]
# Search
query_text = "Find me movies about toys coming alive"

response = rag.search(query_text=query_text, retriever_config={"top_k": 5}, return_context=True)

print(response.answer)
print("CONTEXT:", response.retriever_result.items)
# end::search_return_context[]

# Close the database connection
driver.close()
