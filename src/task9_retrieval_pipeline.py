import logging
from Day08_RAG_pipeline_cohort2.src.task5_semantic_search import semantic_search
from Day08_RAG_pipeline_cohort2.src.task6_lexical_search import lexical_search
from Day08_RAG_pipeline_cohort2.src.task7_reranking import rrf_rerank
from Day08_RAG_pipeline_cohort2.src.task8_pageindex_vectorless import PageIndexSearcher

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class RetrievalPipeline:
    def __init__(self):
        self.pageindex_fallback = PageIndexSearcher()

    def retrieve(self, query: str, top_k: int = 5, score_threshold: float = 0.02) -> list[dict]:
        """
        1. Chạy semantic_search + lexical_search
        2. Merge kết quả (RRF)
        3. Nếu top result score < threshold -> fallback PageIndex
        4. Return top_k results
        """
        logging.info(f"--- ĐANG XỬ LÝ QUERY: '{query}' ---")
        
        # Bước 1: Truy xuất đa luồng (Hybrid Search)
        # Lưu ý: Lấy top_k lớn hơn một chút (vd: 10) để có nhiều candidate cho Reranker
        sem_results = semantic_search(query, top_k=10)
        lex_results = lexical_search(query, top_k=10)
        
        # Bước 2: Rerank và Merge bằng RRF
        reranked_results = rrf_rerank(sem_results, lex_results, top_k=top_k)
        
        # Bước 3: Kiểm tra Threshold (Ngưỡng tự tin)
        # Với thuật toán RRF (k=60), điểm số tối đa cho top 1 ở cả 2 luồng là (1/61 + 1/61) ~ 0.032
        # Nếu điểm top 1 thấp hơn threshold, chứng tỏ DB không có câu trả lời tốt -> kích hoạt Fallback
        best_score = reranked_results[0]['score'] if reranked_results else 0
        
        if best_score < score_threshold or not reranked_results:
            logging.warning(f"Điểm số cao nhất ({best_score:.4f}) dưới ngưỡng ({score_threshold}). Kích hoạt Fallback!")
            return self.pageindex_fallback.pageindex_search(query, top_k=top_k)
            
        logging.info(f"Truy xuất thành công từ DB Cục bộ. Điểm cao nhất: {best_score:.4f}")
        return reranked_results

if __name__ == "__main__":
    pipeline = RetrievalPipeline()
    
    # Test 1: Query có trong DB (Luật ma túy)
    print("\n[TEST 1]")
    res1 = pipeline.retrieve("Tội tàng trữ trái phép chất ma túy phạt bao nhiêu năm tù?")
    print(f"Top 1: {res1[0]['content'][:150]}...\n")
    
    # Test 2: Query rác / Không có trong DB -> Sẽ gọi Fallback
    print("\n[TEST 2]")
    res2 = pipeline.retrieve("Công thức nấu món thịt kho tàu ngon nhất là gì?", score_threshold=0.03)
    print(f"Top 1: {res2[0]['content'][:150]}...")