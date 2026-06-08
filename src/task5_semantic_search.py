import chromadb
from chromadb.utils import embedding_functions

# Khởi tạo connection dùng chung
db_client = chromadb.PersistentClient(path="data/vector_db")
embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="BAAI/bge-m3")
collection = db_client.get_collection(name="drug_law_news", embedding_function=embedding_fn)

def semantic_search(query: str, top_k: int = 10) -> list[dict]:
    """
    Thực hiện Semantic Search sử dụng ChromaDB.
    Returns: List of {'content': str, 'score': float, 'metadata': dict}
    """
    results = collection.query(
        query_texts=[query],
        n_results=top_k,
        include=["documents", "metadatas", "distances"]
    )
    
    formatted_results = []
    # ChromaDB trả về list lồng nhau, ta cần bóc tách
    docs = results['documents'][0]
    metas = results['metadatas'][0]
    distances = results['distances'][0] # Khoảng cách (càng nhỏ càng giống)
    
    for doc, meta, dist in zip(docs, metas, distances):
        # Chuyển đổi distance thành score (càng cao càng tốt) để dễ tính toán sau này
        score = 1.0 / (1.0 + dist) 
        
        formatted_results.append({
            'content': doc,
            'score': float(score),
            'metadata': meta
        })
        
    # Sắp xếp giảm dần theo điểm (dù ChromaDB đã xếp sẵn)
    formatted_results = sorted(formatted_results, key=lambda x: x['score'], reverse=True)
    return formatted_results

if __name__ == "__main__":
    # Test thử
    query = "Hành vi tổ chức sử dụng ma túy bị xử lý như thế nào?"
    res = semantic_search(query, top_k=3)
    print(f"Top 1 Semantic: {res[0]['content'][:100]}... | Score: {res[0]['score']}")