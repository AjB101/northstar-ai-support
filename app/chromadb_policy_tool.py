import chromadb

def initialize_policy_vector_db():
    db_client = chromadb.Client()
    
    # Fix from Usen's Point 3: Use get_or_create_collection
    policy_collection = db_client.get_or_create_collection(
        name="northstar_support_rules"
    )
    
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
    search_results = collection.query(
        query_texts=[user_problem],
        n_results=1
    )
    
    # Fix from Usen's Point 4: Guard the empty-result case
    documents = search_results.get("documents", [])
    if not documents or not documents[0]:
        return None
        
    # Fix from Usen's Point 5: Preserve policy ID/metadata
    metadatas = search_results.get("metadatas", [])
    metadata = metadatas[0][0] if metadatas and metadatas[0] else {}
    
    return {
        "policy_text": documents[0][0],
        "metadata": metadata
    }