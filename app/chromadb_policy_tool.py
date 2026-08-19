import chromadb

def initialize_policy_vector_db():
    # 1. Start the ChromaDB engine for local memory
    db_client = chromadb.Client()
    
    # 2. Create a specific storage container for Northstar's rules
    policy_collection = db_client.create_collection(name="northstar_support_rules")
    
    # 3. Insert the required company guidelines into the database
    policy_collection.add(
        documents=[
            "For double charges, apologize and issue a full refund to the original payment method.",
            "For 500 Internal Server Errors, escalate to Tier 2 Engineering without promising a fix time.",
            "Hardware returns are allowed within 30 days. Send a return label and request original packaging."
        ],
        metadatas=[
            {"category": "Billing"}, 
            {"category": "Technical Support"}, 
            {"category": "Returns"}
        ],
        ids=["rule_1", "rule_2", "rule_3"]
    )
    
    return policy_collection

def fetch_rule_for_ticket(collection, user_problem):
    # Search the vector database for the closest match to the customer's issue
    search_results = collection.query(
        query_texts=[user_problem],
        n_results=1 
    )
    
    # Extract just the plain text string of the policy to pass back to the orchestrator
    found_rule = search_results['documents'][0][0]
    
    return found_rule