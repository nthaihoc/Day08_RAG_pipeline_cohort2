import os
import requests
import logging

# Cấu hình logging để dễ debug
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class LegalDocCollector:
    def __init__(self, output_dir: str = "data/landing/legal"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Danh sách các link PDF mẫu (Bạn có thể thay thế bằng link thực tế tải từ thư viện pháp luật)
        self.target_docs = {
            "luat-phong-chong-ma-tuy-2021.pdf": "https://file1.ttthvn.com/file/VB_BoCongAn/Luat-phong-chong-ma-tuy.pdf",
            "nghi-dinh-105-2021.pdf": "https://file1.ttthvn.com/file/VB_BoCongAn/Nghi-dinh-105-2021-ND-CP.pdf",
            "bo-luat-hinh-su-2015.pdf": "https://file1.ttthvn.com/file/VB_BoCongAn/Bo-luat-hinh-su-2015.pdf"
        }

    def download_file(self, url: str, filename: str):
        filepath = os.path.join(self.output_dir, filename)
        try:
            logging.info(f"Đang tải: {filename}...")
            response = requests.get(url, stream=True, timeout=15)
            response.raise_for_status() # Báo lỗi nếu HTTP status != 200
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            logging.info(f"Thành công: Đã lưu {filename}")
        except Exception as e:
            logging.error(f"Thất bại khi tải {filename}: {e}")
            logging.warning(f"-> Vui lòng tải thủ công file này và lưu vào {filepath}")

    def run(self):
        logging.info("--- BẮT ĐẦU TASK 1: THU THẬP TÀI LIỆU PHÁP LUẬT ---")
        for filename, url in self.target_docs.items():
            self.download_file(url, filename)
        logging.info("--- HOÀN THÀNH TASK 1 ---")

if __name__ == "__main__":
    collector = LegalDocCollector()
    collector.run()