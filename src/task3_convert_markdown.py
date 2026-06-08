import os
import json
import logging
from markitdown import MarkItDown

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DocumentStandardizer:
    def __init__(self, landing_dir: str = "data/landing", standardized_dir: str = "data/standardized"):
        self.landing_dir = landing_dir
        self.standardized_dir = standardized_dir
        self.md = MarkItDown()

    def process_directory(self):
        logging.info("--- BẮT ĐẦU TASK 3: CHUẨN HÓA MARKDOWN ---")
        
        # Duyệt qua các thư mục con (legal, news)
        for root, dirs, files in os.walk(self.landing_dir):
            for file in files:
                input_path = os.path.join(root, file)
                
                # Tạo thư mục đích tương ứng (giữ nguyên cấu trúc legal/news)
                relative_path = os.path.relpath(root, self.landing_dir)
                output_folder = os.path.join(self.standardized_dir, relative_path)
                os.makedirs(output_folder, exist_ok=True)
                
                # Định nghĩa tên file output (đổi đuôi thành .md)
                base_name = os.path.splitext(file)[0]
                output_path = os.path.join(output_folder, f"{base_name}.md")
                
                self.convert_to_markdown(input_path, output_path)
                
        logging.info("--- HOÀN THÀNH TASK 3 ---")

    def convert_to_markdown(self, input_path: str, output_path: str):
        try:
            # Xử lý riêng cho file JSON từ Task 2 (vì MarkItDown xử lý trực tiếp JSON đôi khi bị nhiễu ngoặc nhọn)
            if input_path.endswith('.json'):
                with open(input_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Ghép Metadata làm Header của file Markdown
                md_content = f"# {data['metadata']['title']}\n"
                md_content += f"- **Nguồn:** {data['metadata']['source_url']}\n"
                md_content += f"- **Ngày cào:** {data['metadata']['crawled_at']}\n\n"
                md_content += data['content']
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(md_content)
                logging.info(f"Đã convert JSON: {os.path.basename(output_path)}")
                
            # Xử lý PDF/DOCX từ Task 1 bằng MarkItDown
            elif input_path.endswith(('.pdf', '.docx', '.pptx', '.xlsx')):
                result = self.md.convert(input_path)
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(result.text_content)
                logging.info(f"Đã convert Document: {os.path.basename(output_path)}")
                
        except Exception as e:
            logging.error(f"Lỗi khi convert {input_path}: {e}")

if __name__ == "__main__":
    standardizer = DocumentStandardizer()
    standardizer.process_directory()