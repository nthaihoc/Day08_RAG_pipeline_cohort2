import os
import logging
from dotenv import load_dotenv
from openai import OpenAI
from Day08_RAG_pipeline_cohort2.src.task9_retrieval_pipeline import RetrievalPipeline

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class GenerationPipeline:
    def __init__(self):
        # Khởi tạo OpenAI client (đảm bảo đã có OPENAI_API_KEY trong .env)
        self.client = OpenAI()
        self.retriever = RetrievalPipeline()
        
        self.system_prompt = """You are a legal and news assistant specializing in Vietnamese drug laws and related news. 
Answer the following question comprehensively based ONLY on the provided context.
For every statement of fact or claim, immediately insert a citation in brackets linking to the specific source provided in the context (e.g., [Luat-phong-chong-ma-tuy-2021.md]).
If the information is not explicitly stated in the provided context, state 'I cannot verify this information' rather than guessing.
Always reply in Vietnamese."""

    def reorder_for_llm(self, chunks: list[dict]) -> list[dict]:
        """
        Sắp xếp chunks theo pattern: quan trọng nhất ở đầu và cuối, ít quan trọng hơn ở giữa.
        Đầu vào (đã sort giảm dần): [1, 2, 3, 4, 5]
        Đầu ra: [1, 3, 5, 4, 2]
        """
        if not chunks:
            return []
            
        reordered = []
        # Chạy từ đầu đến cuối, chẵn cho lên đầu, lẻ cho xuống đuôi
        for i, chunk in enumerate(chunks):
            if i % 2 == 0:
                reordered.insert(0, chunk) # Nhét vào đầu
            else:
                reordered.append(chunk) # Nhét vào cuối
        return reordered

    def generate_with_citation(self, query: str) -> dict:
        logging.info("Bắt đầu Retrieve & Generate...")
        
        # 1. Retrieve data từ Task 9
        retrieved_chunks = self.retriever.retrieve(query, top_k=5)
        
        # 2. Reorder để tránh Lost in the Middle
        reordered_chunks = self.reorder_for_llm(retrieved_chunks)
        
        # 3. Format context
        context_text = ""
        for idx, chunk in enumerate(reordered_chunks):
            source = chunk['metadata'].get('source_file', 'Unknown_Source')
            content = chunk['content']
            context_text += f"\n--- TÀI LIỆU {idx + 1} | Nguồn: [{source}] ---\n{content}\n"

        # 4. Inject vào Prompt
        user_prompt = f"Ngữ cảnh (Context):\n{context_text}\n\nCâu hỏi (Query): {query}"
        
        try:
            # 5. Gọi LLM
            # Dùng top_p = 0.1 và temperature = 0.1 để câu trả lời bám sát context, không hallucination
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo", # Hoặc gpt-4o-mini
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                top_p=0.1
            )
            
            answer = response.choices[0].message.content
            
            return {
                "answer": answer,
                "sources": retrieved_chunks # Trả về list ban đầu để hiển thị lên UI
            }
            
        except Exception as e:
            logging.error(f"Lỗi khi gọi LLM: {e}")
            return {"answer": "Xin lỗi, đã có lỗi xảy ra trong quá trình tạo câu trả lời.", "sources": []}

if __name__ == "__main__":
    generator = GenerationPipeline()
    res = generator.generate_with_citation("Tội tàng trữ trái phép chất ma túy phạt bao nhiêu năm tù?")
    print("\n--- CÂU TRẢ LỜI ---")
    print(res["answer"])