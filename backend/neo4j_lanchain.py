from flask import Flask, request, jsonify
from flask_cors import CORS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_neo4j import GraphCypherQAChain, Neo4jGraph
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Load environment variables
load_dotenv()

# Detailed Cypher Generation Template
CYPHER_GENERATION_TEMPLATE = """Task: Generate a precise Cypher statement for querying a Neo4j graph database.

Constraints:
- Use ONLY the relationships and properties defined in the schema
- Avoid using any relationships or properties not explicitly provided
- Generate a valid and efficient Cypher query
- Return meaningful results based on the question

Schema:
{schema}

Examples:
1. Question: How many actors played in Top Gun?
   Cypher: MATCH (m:Movie {{name:"Top Gun"}})<-[:ACTED_IN]-(a:Actor)
           RETURN count(a) AS numberOfActors

2. Question: List all actors in Top Gun
   Cypher: MATCH (m:Movie {{name:"Top Gun"}})<-[:ACTED_IN]-(a:Actor)
           RETURN a.name AS ActorNames

Question to convert to Cypher: {question}

Cypher Query:"""

CYPHER_GENERATION_PROMPT = PromptTemplate(
    input_variables=["schema", "question"],
    template=CYPHER_GENERATION_TEMPLATE
)

def init_chain():
    graph = Neo4jGraph(
        url="neo4j://localhost:7687",
        username="neo4j",
        password="password",
        refresh_schema=True
    )
    
    
    model = ChatGoogleGenerativeAI(model="gemini-1.5-pro")
    
    return GraphCypherQAChain.from_llm(
        graph=graph,
        llm=model,
        verbose=True,
        cypher_prompt=CYPHER_GENERATION_PROMPT,
        allow_dangerous_requests=True
    )

@app.route('/api/query', methods=['POST'])
def handle_query():
    try:
        data = request.json
        query = data.get('query')
        
        if not query:
            return jsonify({'error': 'No query provided'}), 400
            
        chain = init_chain()
        response = chain.invoke({"query": query})
        
        return jsonify({
            'response': response,
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)