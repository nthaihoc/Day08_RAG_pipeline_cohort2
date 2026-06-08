import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def rrf_rerank(semantic_results: list[dict], lexical_results: list[dict], top_k: int = 5, rrf_k: int = 60) -> list[dict]:
    """
    Thực hiện gộp và chấm điểm lại bằng thuật toán Reciprocal Rank Fusion (RRF).
    Công thức: RRF_Score = 1 / (rrf_k + rank)
    """
    logging.info("Đang thực hiện Reranking bằng thuật toán RRF...")
    
    rrf_scores = {}
    combined_docs = {}

    # Hàm xử lý chung để tính RRF cho từng danh sách kết quả
    def compute_rrf(results_list):
        for rank, item in enumerate(results_list):
            doc_content = item['content']
            # Dùng nội dung làm key (hoặc có thể dùng ID nếu bạn đã lưu ID ở task 4)
            if doc_content not in rrf_scores:
                rrf_scores[doc_content] = 0.0
                combined_docs[doc_content] = item
                
            # Cộng dồn điểm RRF
            rrf_scores[doc_content] += 1.0 / (rrf_k + rank + 1)

    # 1. Tính điểm cho Semantic Search
    compute_rrf(semantic_results)
    
    # 2. Tính điểm cho Lexical Search (BM25)
    compute_rrf(lexical_results)

    # 3. Sắp xếp lại dựa trên điểm RRF tổng hợp
    reranked_results = []
    for doc_content, score in rrf_scores.items():
        doc_info = combined_docs[doc_content].copy()
        doc_info['score'] = score # Cập nhật lại score thành score của RRF
        reranked_results.append(doc_info)

    # Trả về danh sách đã sắp xếp giảm dần
    reranked_results = sorted(reranked_results, key=lambda x: x['score'], reverse=True)
    return reranked_results[:top_k]

if __name__ == "__main__":
    # Test thử thuật toán với dữ liệu giả
    sem_mock = [{'content': 'A', 'score': 0.9, 'metadata': {}}, {'content': 'B', 'score': 0.8, 'metadata': {}}]
    lex_mock = [{'content': 'C', 'score': 2.1, 'metadata': {}}, {'content': 'A', 'score': 1.5, 'metadata': {}}]
    
    res = rrf_rerank(sem_mock, lex_mock)
    print("Kết quả RRF Rerank:", [r['content'] for r in res]) 
    # Document 'A' xuất hiện ở cả 2 nơi nên sẽ có điểm cao nhất và xếp đầu.