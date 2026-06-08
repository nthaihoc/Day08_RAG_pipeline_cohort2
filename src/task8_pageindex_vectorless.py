import os
import logging
from dotenv import load_dotenv
# from pageindex import Client # Giả định SDK của pageindex

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class PageIndexSearcher:
    def __init__(self):
        self.api_key = os.getenv("PAGEINDEX_API_KEY", "YOUR_API_KEY_HERE")
        # Khởi tạo client thực tế ở đây
        # self.client = Client(api_key=self.api_key)
        logging.info("Khởi tạo PageIndex Vectorless Searcher.")

    def pageindex_search(self, query: str, top_k: int = 5) -> list[dict]:
        """
        Vectorless retrieval using PageIndex.
        Fallback khi hybrid search không trả về kết quả phù hợp.
        """
        logging.warning(f"Kích hoạt Fallback PageIndex cho query: '{query}'")
        
        # --- ĐOẠN CODE GỌI API THỰC TẾ (MOCK) ---
        # response = self.client.search(query=query, top_k=top_k)
        # formatted_results = [{'content': r.text, 'score': r.score, 'metadata': r.meta} for r in response]
        
        # Vì chúng ta chưa có tài khoản/tài liệu upload lên server PageIndex, tôi trả về mock data
        formatted_results = [
            {
                'content': "Đây là kết quả trả về từ hệ thống dự phòng PageIndex (Vectorless).",
                'score': 1.0,
                'metadata': {'source': 'PageIndex API'}
            }
        ]
        return formatted_results

if __name__ == "__main__":
    searcher = PageIndexSearcher()
    print(searcher.pageindex_search("Chi Dân"))