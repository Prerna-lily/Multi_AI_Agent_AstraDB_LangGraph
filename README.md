**LangGraph_AstraDB**

Overview

This project demonstrates how to use LangGraph with AstraDB for document retrieval and AI agent applications. It involves building a vector database using AstraDB, embedding documents with HuggingFace, implementing a retrieval system, and routing user queries between a vector store and Wikipedia using a structured LLM router.

**Features**

Document Indexing & Retrieval: Uses AstraDB as a vector store to index and retrieve documents.

LLM Integration: Routes user queries to a vector store or Wikipedia search using an LLM-based router.

AI Agent Graph Workflow: Implements a LangGraph-based workflow for question answering.

HuggingFace Embeddings: Utilizes all-MiniLM-L6-v2 embeddings for vector search.

Wikipedia API Integration: Fetches Wikipedia content for non-indexed queries.

LangGraph Workflow: Defines a state graph to determine the best retrieval source.

**Dependencies**

Install the required dependencies using:

pip install langchain langgraph cassio langchain_community tiktoken langchain-groq langchainhub chromadb langchain_huggingface wikipedia

**Setup**

**Connect to AstraDB:**

Set up AstraDB credentials:

import cassio
ASTRA_DB_APPLICATION_TOKEN="your_token_here"
ASTRA_DB_ID="your_db_id_here"
cassio.init(token=ASTRA_DB_APPLICATION_TOKEN, database_id=ASTRA_DB_ID)

Load Documents for Indexing:

Fetch articles from IBM and Wikipedia, split them into chunks, and index them into AstraDB.

Initialize Vector Store:

from langchain.vectorstores.cassandra import Cassandra
astra_vector_store = Cassandra(embedding=embeddings, table_name="qa_mini_demo")
astra_vector_store.add_documents(docs_split)

Query Routing & Processing:

Uses an LLM (ChatGroq) to determine whether to search Wikipedia or AstraDB.

from langchain_groq import ChatGroq
llm = ChatGroq(groq_api_key='your_api_key', model_name="llama-3.3-70b-versatile")

Define AI Agent Workflow:

Uses LangGraph to create a structured workflow for querying either Wikipedia or the vector store.

from langgraph.graph import StateGraph
workflow = StateGraph(GraphState)
workflow.add_node("wiki_search", search_wiki)
workflow.add_node("vectorstore", retrieve)

Running the Project

Execute the main script to test the retrieval system and workflow:

inputs = { "question": "What are LLMs?" }
for output in app.stream(inputs):
    print(output)

**Outputs**

The system retrieves relevant documents from AstraDB or Wikipedia.

The LangGraph visualization illustrates the workflow execution.

The final output includes a relevant response based on the query routing.

Future Improvements

Extend document sources for better coverage.

Improve retrieval accuracy using advanced ranking techniques.

Implement a UI for user-friendly interaction.

License

This project is open-source and available for use under the MIT License.

