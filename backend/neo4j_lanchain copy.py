from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_neo4j import GraphCypherQAChain, Neo4jGraph
from dotenv import load_dotenv
import os
import getpass

# Load environment variables
load_dotenv()

# Prompt for API key if not set in environment
if "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = getpass.getpass("Enter your Google AI API key: ")

# Initialize Google Generative AI model
model = ChatGoogleGenerativeAI(model="gemini-1.5-pro")

# Main block
try:
    # Establish Neo4j connection
    graph = Neo4jGraph(
        url="neo4j://localhost:7687",
        username="neo4j",
        password="password",
        refresh_schema=False
    )
    
    # Create data
    graph.query("""
        MERGE (m:Movie {name:"Top Gun", runtime: 120})
        WITH m
        UNWIND ["Tom Cruise", "Val Kilmer", "Anthony Edwards", "Meg Ryan"] AS actor
        MERGE (a:Actor {name:actor})
        MERGE (a)-[:ACTED_IN]->(m)
    """)
    
    # Refresh schema and print
    graph.refresh_schema()
    print(graph.schema)
    
    # Test query to find all actors in Top Gun
    result = graph.query("""
    MATCH (a:Actor)-[:ACTED_IN]->(m:Movie {name: 'Top Gun'})
    RETURN a.name as actor
    """)
    print("Actors in 'Top Gun':", result)

    # Test query to get movie details
    result = graph.query("""
    MATCH (m:Movie {name: 'Top Gun'})
    RETURN m.name, m.runtime
    """)
    print("Movie details:", result)

    chain = GraphCypherQAChain.from_llm(
    graph=graph, llm=model, verbose=True, allow_dangerous_requests=True
)

    response = chain.invoke({"query": "what movie tom cruise acted in?"})
    print("Response from chain:", response)

finally:
    # Close connection
    graph.close()


