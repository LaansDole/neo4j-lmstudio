import os

from dotenv import load_dotenv

load_dotenv()

# end::import_text2cypher[]
from lmstudio_client import get_chat_model, get_lmstudio_llm, client
from neo4j import GraphDatabase
from neo4j_graphrag.generation import GraphRAG
from neo4j_graphrag.llm import LLMInterface

# tag::import_text2cypher[]
from neo4j_graphrag.retrievers import Text2CypherRetriever

# Connect to Neo4j database
driver = GraphDatabase.driver(os.getenv("NEO4J_URI"), auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD")))


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


# tag::t2c_llm[]
# Create Cypher LLM with LM Studio
t2c_llm = LMStudioLLM(get_chat_model())
# end::t2c_llm[]

# tag::retriever[]
# Build the retriever
retriever = Text2CypherRetriever(
    driver=driver,
    llm=t2c_llm,
)
# end::retriever[]

llm = LMStudioLLM(get_chat_model())
rag = GraphRAG(retriever=retriever, llm=llm)

query_text = "Which movies did Hugo Weaving acted in?"
query_text = "What are examples of Action movies?"

response = rag.search(query_text=query_text, return_context=True)

print(response.answer)
print("CYPHER :", response.retriever_result.metadata["cypher"])
print("CONTEXT:", response.retriever_result.items)

driver.close()

query_text = "Which movies did Hugo Weaving acted in?"
query_text = "What are examples of Action movies?"

response = rag.search(query_text=query_text, return_context=True)

print(response.answer)
print("CYPHER :", response.retriever_result.metadata["cypher"])
print("CONTEXT:", response.retriever_result.items)

driver.close()
