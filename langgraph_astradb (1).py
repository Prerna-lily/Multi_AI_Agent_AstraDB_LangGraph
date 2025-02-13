# -*- coding: utf-8 -*-
"""LangGraph_AstraDB.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1sRS8oyL2xe2mPMAH7Y4AcPtz5YimJW60
"""

!pip install langchain langgraph cassio

import cassio
#connection of the astra db
ASTRA_DB_APPLICATION_TOKEN=""
ASTRA_DB_ID=""
cassio.init(token=ASTRA_DB_APPLICATION_TOKEN,database_id= ASTRA_DB_ID)

!pip install langchain_community

!pip install -U tiktoken langchain-groq langchainhub chromadb langchain langgraph langchain_huggingface

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader

#build index
#docs to index
urls=[
    "https://www.ibm.com/think/topics/ai-agents",
    "https://www.ibm.com/think/topics/large-language-models",
    "https://en.wikipedia.org/wiki/Generative_artificial_intelligence"
]
#load url[
docs= [WebBaseLoader(url).load() for url in urls]
doc_list = [item for sublist in docs for item in sublist]
print(doc_list)
textsplitter=RecursiveCharacterTextSplitter.from_tiktoken_encoder(chunk_size=500,chunk_overlap=0)
docs_split = textsplitter.split_documents(doc_list)

docs_split

from langchain_huggingface import HuggingFaceEmbeddings
embeddings=HuggingFaceEmbeddings(model_name='all-MiniLM-L6-v2')

from langchain.vectorstores.cassandra import Cassandra
astra_vector_store = Cassandra(embedding=embeddings,
                               table_name="qa_mini_demo",
                               session=None,
                               keyspace=None)

from langchain.indexes.vectorstore import VectorStoreIndexWrapper
astra_vector_store.add_documents(docs_split)
print("Inserted %i headlines: "%len(docs_split))
astra_vector_index=VectorStoreIndexWrapper(vectorstore=astra_vector_store)

#retrieve the information
retriever = astra_vector_store.as_retriever()
retriever.invoke("What are LLMs")

#langgraph application
from typing import Literal

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field

#Data model
class RouteQuery(BaseModel):
  """Route a user query to the most relevant data source"""
  datasource: Literal["vectorstore","wiki-search"]=Field(
      ...,
      description="Given a user question choose to route it to wikipedia or a vectorstore.",
  )

from google.colab import userdata
import os
from langchain_groq import ChatGroq
groq_api_key = userdata.get('groq_api_key')
print(groq_api_key)

llm=ChatGroq(groq_api_key=groq_api_key,model_name="llama-3.3-70b-versatile")
llm

structured_llm_router=llm.with_structured_output(RouteQuery)

#prompt
system="You are an expert at routing user question to a vectorstore or wikipedia. The vectorstore contains documents related to agents, prompt engineering and adversarial attacks. Use the vectorstore for questions on these topics. Otherwise use wiki-search."
route_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human", "{question}"),
    ]
)
question_router = route_prompt | structured_llm_router

print(question_router.invoke({"question":"What are LLMs"}))

print(question_router.invoke({"question":"Who is Narendra Modi"}))

!pip install wikipedia

from langchain_community.utilities import WikipediaAPIWrapper
from langchain_community.tools import WikipediaQueryRun
api_wrapper = WikipediaAPIWrapper(top_k_results=1,doc_content_chars_max=200)
wiki = WikipediaQueryRun(api_wrapper=api_wrapper)

wiki.run("Tell me about Singer Selena Gomez")

#AI agents application using LangGraph
from typing import List
from typing_extensions import TypedDict

class GraphState(TypedDict):
  """
  Represents the state of the graph.
  Attributes:
  question: question generation
  llm: llm generation
  documents: documents generation
  """
  question: str
  generation: str
  documents: List[str]

from langchain.schema import Document
#query it from the retriever and display it
def retrieve(state):
  """
    Retrieval
    Args:
      state: GraphState
    Returns:
      new key added to state, documents, that contain the retrieved documents
  """
  print("Retrieve: ")
  question = state["question"]
  #retrieval
  documents = retriever.invoke(question)
  return {"documents": documents, "question": question}

#for wikipedia search
def search_wiki(state):
  print("Wikipidea: ")
  question = state["question"]
  print(question)

  #wiki search
  docs = wiki.invoke({'query':question})
  wiki_results = docs
  wiki_results = Document(page_content=wiki_results)
  return {"documents": [wiki_results], "question": question}

def route_question(state):
  """
  route question to wiki search or RAG
  args:
  the current graph state
  returns:
  str: Next node to call
  """
  print("Route question:")
  question = state["question"]
  source = question_router.invoke({"question":question})
  if source.datasource == "wiki_search":
    print("Route question to wiki search")
    return "wiki_search"
  elif source.datasource == "vectorstore":
    print("Route question to RAG")
    return "vectorstore"

from langgraph.graph import StateGraph, START, END
workflow = StateGraph(GraphState)
#define the nodes
workflow.add_node("wiki_search",search_wiki) #web search
workflow.add_node("vectorstore",retrieve) #retrieve
#build the graph
workflow.add_conditional_edges(
    START,
    route_question,
    {
        "wiki_search":"wiki_search",
        "vectorstore":"vectorstore" # Changed 'retrieve' to 'vectorstore'
    }
)
workflow.add_edge("vectorstore",END) # Changed 'retrieve' to 'vectorstore'
workflow.add_edge("wiki_search",END)
#compile
app = workflow.compile()

from IPython.display import Image, display
try:
  display(Image(app.get_graph().draw_mermaid_png()))
except:
  Exception

from pprint import pprint

# Run
inputs = {
    "question": "What is agent?"
}
for output in app.stream(inputs):
    for key, value in output.items():
        # Node
        pprint(f"Node '{key}':")
        # Optional: print full state at each node
        # pprint.pprint(value["keys"], indent=2, width=80, depth=None)
    pprint("\n---\n")

# Final generation
pprint(value['documents'][0].dict()['metadata']['description'])

