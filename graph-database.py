# # import dotenv
# # import os
# # from py2neo import Graph
# #
# # load_status = dotenv.load_dotenv("Neo4j-a3fcb40c-Created-2025-01-27.txt")
# # if load_status is False:
# #     raise RuntimeError('Environment variables not loaded.')
# #
# # URI = os.getenv("NEO4J_URI")
# # AUTH = (os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))
# #
# # # connect to database
# # graph = Graph(URI, auth=AUTH)
#
# import dotenv
# import os
# from neo4j import GraphDatabase
# import json
#
# load_status = dotenv.load_dotenv("Neo4j-a3fcb40c-Created-2025-01-27.txt")
# if load_status is False:
#     raise RuntimeError('Environment variables not loaded.')
#
# URI = os.getenv("NEO4J_URI")
# AUTH = (os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))
#
# graph = GraphDatabase.driver(URI, auth=AUTH)
#
# try:
#     graph.run("Match () Return 1 Limit 1")
#     print('ok')
# except Exception:
#     print('not ok')

import dotenv
import os
from neo4j import GraphDatabase

# Use verify_connectivity() method to ensure that a working connection can be established with a 'Driver' instance
load_status = dotenv.load_dotenv("Neo4j-a3fcb40c-Created-2025-01-27.txt")
if load_status is False:
    raise RuntimeError('Environment variables not loaded.')

URI = os.getenv("NEO4J_URI")
AUTH = (os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))

print(URI)
print(AUTH)

# with GraphDatabase.driver(URI, auth=AUTH) as driver:
#     driver.verify_connectivity()
#     print("Connection established.")