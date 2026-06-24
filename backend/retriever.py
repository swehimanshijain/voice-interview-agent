import json
import chromadb
from sentence_transformers import SentenceTransformer
from typing import Dict, List, Optional

# Initialize models
model = SentenceTransformer("all-MiniLM-L6-v2")
client = chromadb.PersistentClient(path="chroma_db")
collection = client.get_or_create_collection(name="interview_qa")

def load_dataset() -> List[Dict]:
    """Load QA dataset from file"""
    try:
        with open("dataset/qa_dataset.json", "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        print("Dataset not found! Using fallback data.")
        return get_fallback_dataset()

def get_fallback_dataset():
    """Fallback dataset if file not found"""
    return [
        {
            "id": 1,
            "domain": "HR",
            "question": "Tell me about yourself.",
            "ideal_answer": "I'm a software engineer with experience...",
            "key_points": ["Experience", "Skills", "Goals"],
            "follow_up_examples": ["Tell me more about your experience"]
        }
    ]

def build_database():
    """Build ChromaDB from dataset"""
    data = load_dataset()
    
    if collection.count() > 0:
        print(f"Database already exists with {collection.count()} entries.")
        return
    
    for item in data:
        embedding = model.encode(item["question"]).tolist()
        
        collection.add(
            ids=[str(item["id"])],
            embeddings=[embedding],
            documents=[f"Question: {item['question']}"],
            metadatas=[{
                "question": item["question"],
                "domain": item["domain"],
                "ideal_answer": item["ideal_answer"],
                "key_points": ", ".join(item.get("key_points", [])),
                "follow_ups": " | ".join(item.get("follow_up_examples", []))
            }]
        )
    
    print(f"Successfully stored {len(data)} questions in database.")

def get_reference(question: str) -> Dict:
    """Retrieve the most relevant QA pair for a question"""
    try:
        embedding = model.encode(question).tolist()
        
        result = collection.query(
            query_embeddings=[embedding],
            n_results=1
        )
        
        if result["metadatas"] and len(result["metadatas"][0]) > 0:
            metadata = result["metadatas"][0][0]
            return {
                "question": metadata.get("question", question),
                "domain": metadata.get("domain", "General"),
                "ideal_answer": metadata.get("ideal_answer", ""),
                "key_points": metadata.get("key_points", ""),
                "follow_ups": metadata.get("follow_ups", "")
            }
    except Exception as e:
        print(f"Retrieval error: {e}")
    
    # Fallback: return the question as-is
    return {
        "question": question,
        "domain": "General",
        "ideal_answer": "Please provide a comprehensive answer.",
        "key_points": "Clarity, depth, relevance",
        "follow_ups": ""
    }