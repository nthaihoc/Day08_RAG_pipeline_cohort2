import os
import json
import asyncio
import logging
from datetime import datetime
from crawl4ai import AsyncWebCrawler

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class NewsCrawler:
    def __init__(self, output_dir: str = "data/landing/news"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 5 bài báo thực tế về nghệ sĩ và ma túy
        self.urls = [
            "https://vnexpress.net/ca-si-chi-dan-bi-bat-vi-nghi-lien-quan-ma-tuy-4813589.html",
            "https://tuoitre.vn/ca-si-chi-dan-nguoi-mau-an-tay-bi-bat-vi-to-chuc-su-dung-ma-tuy-20241110161435213.htm",
            "https://thanhnien.vn/dien-vien-huu-tin-lanh-an-7-nam-6-thang-tu-vi-to-chuc-su-dung-ma-tuy-18523041713430155.htm",
            "https://vnexpress.net/dien-vien-chau-viet-cuong-bi-tuyen-13-nam-tu-3891461.html",
            "https://dantri.com.vn/phap-luat/nhieu-nghe-si-dinh-vong-lao-ly-vi-ma-tuy-20241111103324567.htm"
        ]

    async def crawl_article(self, crawler: AsyncWebCrawler, url: str, index: int):
        logging.info(f"Đang cào dữ liệu bài {index}: {url}")
        try:
            result = await crawler.arun(url=url)
            
            # Trích xuất metadata và nội dung
            article_data = {
                "metadata": {
                    "source_url": url,
                    "crawled_at": datetime.now().isoformat(),
                    "title": result.metadata.get('title', f"News Article {index}") if result.metadata else f"Article {index}"
                },
                "content": result.markdown # Lấy luôn markdown từ crawl4ai cho sạch
            }
            
            # Lưu ra file JSON
            filename = f"news_article_{index}.json"
            filepath = os.path.join(self.output_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(article_data, f, ensure_ascii=False, indent=4)
                
            logging.info(f"Đã lưu thành công: {filename}")
        except Exception as e:
            logging.error(f"Lỗi khi cào {url}: {e}")

    async def run(self):
        logging.info("--- BẮT ĐẦU TASK 2: CRAWL BÁO CHÍ ---")
        async with AsyncWebCrawler() as crawler:
            tasks = [self.crawl_article(crawler, url, idx + 1) for idx, url in enumerate(self.urls)]
            await asyncio.gather(*tasks) # Chạy song song tất cả các url
        logging.info("--- HOÀN THÀNH TASK 2 ---")

if __name__ == "__main__":
    crawler = NewsCrawler()
    asyncio.run(crawler.run())