import chromadb
from rank_bm25 import BM25Okapi

# Lấy toàn bộ chunks từ ChromaDB để đảm bảo đồng bộ với Semantic Search
db_client = chromadb.PersistentClient(path="data/vector_db")
collection = db_client.get_collection(name="drug_law_news")

# Lấy toàn bộ dữ liệu hiện có trong DB (không dùng query)
all_data = collection.get(include=["documents", "metadatas"])
corpus_docs = all_data["documents"]
corpus_metas = all_data["metadatas"]

# Khởi tạo BM25 (Tokenize đơn giản bằng cách tách khoảng trắng cho tiếng Việt)
tokenized_corpus = [doc.lower().split() for doc in corpus_docs]
bm25_model = BM25Okapi(tokenized_corpus)

def lexical_search(query: str, top_k: int = 10) -> list[dict]:
    """
    Thực hiện tìm kiếm BM25 (Lexical Search).
    Returns: List of {'content': str, 'score': float, 'metadata': dict}
    """
    tokenized_query = query.lower().split()
    
    # Lấy điểm số của query đối với toàn bộ tập tài liệu
    scores = bm25_model.get_scores(tokenized_query)
    
    # Kết hợp thông tin
    results = []
    for idx, score in enumerate(scores):
        if score > 0: # Chỉ lấy các doc có điểm số > 0
            results.append({
                'content': corpus_docs[idx],
                'score': float(score),
                'metadata': corpus_metas[idx]
            })
            
    # Sắp xếp giảm dần theo điểm
    results = sorted(results, key=lambda x: x['score'], reverse=True)
    
    # Trả về top K
    return results[:top_k]

if __name__ == "__main__":
    # Test thử
    query = "ca sĩ chi dân"
    res = lexical_search(query, top_k=3)
    if res:
        print(f"Top 1 Lexical: {res[0]['content'][:100]}... | Score: {res[0]['score']}")
    else:
        print("Không tìm thấy kết quả BM25.")