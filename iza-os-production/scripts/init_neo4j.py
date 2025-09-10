"""
Initialize Neo4j database with repository schema
"""

from neo4j import GraphDatabase
import os

def init_neo4j_schema():
    """Initialize Neo4j with repository-focused schema"""
    
    driver = GraphDatabase.driver(
        "bolt://localhost:7687",
        auth=("neo4j", os.getenv("NEO4J_PASSWORD", "password"))
    )
    
    with driver.session() as session:
        # Create constraints
        constraints = [
            "CREATE CONSTRAINT repo_name IF NOT EXISTS FOR (r:Repository) REQUIRE r.name IS UNIQUE",
            "CREATE CONSTRAINT file_path IF NOT EXISTS FOR (f:File) REQUIRE f.path IS UNIQUE",
            "CREATE CONSTRAINT user_login IF NOT EXISTS FOR (u:User) REQUIRE u.login IS UNIQUE",
            "CREATE CONSTRAINT commit_hash IF NOT EXISTS FOR (c:Commit) REQUIRE c.hash IS UNIQUE"
        ]
        
        for constraint in constraints:
            try:
                session.run(constraint)
                print(f"✅ Created constraint: {constraint}")
            except Exception as e:
                print(f"⚠️ Constraint already exists or error: {e}")
        
        # Create indexes
        indexes = [
            "CREATE INDEX repo_language IF NOT EXISTS FOR (r:Repository) ON (r.language)",
            "CREATE INDEX repo_stars IF NOT EXISTS FOR (r:Repository) ON (r.stars)",
            "CREATE INDEX file_extension IF NOT EXISTS FOR (f:File) ON (f.extension)",
            "CREATE INDEX commit_date IF NOT EXISTS FOR (c:Commit) ON (c.date)"
        ]
        
        for index in indexes:
            try:
                session.run(index)
                print(f"✅ Created index: {index}")
            except Exception as e:
                print(f"⚠️ Index already exists or error: {e}")
    
    driver.close()
    print("🗃️ Neo4j schema initialization complete!")

if __name__ == "__main__":
    init_neo4j_schema()
