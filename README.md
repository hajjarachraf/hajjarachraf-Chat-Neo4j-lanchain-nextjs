
npm  v10.8.2
node v20.11.0
python v3.12.2

to start 

lunch Neo4j in docker (or Neo4j Desktop)

docker run ^
    --name neo4j ^
    -p 7474:7474 -p 7687:7687 ^
    -d ^
    -e NEO4J_AUTH=neo4j/12345678 ^
    -e NEO4J_PLUGINS="['apoc']" ^
    neo4j:latest

backend : install requirement for python
          python neo4j_lanchain.py

frontendNextJs : npm install 
                 npm run dev