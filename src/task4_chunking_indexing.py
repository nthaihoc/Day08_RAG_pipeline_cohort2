import os
import uuid
import logging
from typing import List
import chromadb
from chromadb.utils import embedding_functions
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DocumentIndexer:
    def __init__(self, input_dir: str = "data/standardized", db_dir: str = "data/vector_db"):
        self.input_dir = input_dir
        
        # Khởi tạo ChromaDB lưu trữ cục bộ
        os.makedirs(db_dir, exist_ok=True)
        self.chroma_client = chromadb.PersistentClient(path=db_dir)
        
        # Khởi tạo Embedding model (BAAI/bge-m3 dimension=1024)
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="BAAI/bge-m3")
        
        # Xóa collection cũ nếu chạy lại
        try:
            self.chroma_client.delete_collection(name="drug_law_news")
        except:
            pass
            
        self.collection = self.chroma_client.create_collection(
            name="drug_law_news", 
            embedding_function=self.embedding_fn
        )

    def process_and_index(self):
        logging.info("--- BẮT ĐẦU TASK 4: CHUNKING & INDEXING ---")
        
        # 1. Cấu hình Splitters
        headers_to_split_on = [("#", "Header 1"), ("##", "Header 2"), ("###", "Header 3")]
        markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        
        # 2. Đọc file và cắt
        all_chunks = []
        all_metadatas = []
        all_ids = []

        for root, dirs, files in os.walk(self.input_dir):
            for file in files:
                if not file.endswith(".md"): continue
                
                filepath = os.path.join(root, file)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Cắt theo Markdown Heading trước
                md_splits = markdown_splitter.split_text(content)
                
                # Cắt tiếp theo độ dài ký tự
                chunks = text_splitter.split_documents(md_splits)
                
                for chunk in chunks:
                    all_chunks.append(chunk.page_content)
                    
                    # Bổ sung metadata nguồn
                    meta = chunk.metadata
                    meta["source_file"] = file
                    all_metadatas.append(meta)
                    
                    all_ids.append(str(uuid.uuid4()))

        # 3. Indexing vào ChromaDB
        logging.info(f"Đã tạo {len(all_chunks)} chunks. Tiến hành nhúng (Embedding) vào ChromaDB...")
        
        # ChromaDB khuyên nên add theo batch nhỏ nếu dữ liệu lớn (ở đây < 5000 chunks có thể add luôn)
        self.collection.add(
            documents=all_chunks,
            metadatas=all_metadatas,
            ids=all_ids
        )
        
        logging.info("--- HOÀN THÀNH TASK 4 ---")

if __name__ == "__main__":
    indexer = DocumentIndexer()
    indexer.process_and_index()