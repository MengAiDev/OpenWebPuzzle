import json
import random
import re
from datasets import load_dataset
from transformers import pipeline
from tqdm.auto import tqdm  # 兼容Jupyter和脚本
import torch

# 设置随机种子保证可复现
random.seed(42)
torch.manual_seed(42)

# 1. 基础数据源 - 使用公开本地化数据集
def load_base_data():
    """Load public text datasets as base corpus"""
    print("Loading base datasets...")
    # 使用C4数据集 (Colossal Cleaned Crawl)
    c4_data = list(load_dataset("allenai/c4", "en", split="train", streaming=True, trust_remote_code=True).take(5000))
    
    # 使用ArXiv论文摘要 (科学类内容)
    try:
        arxiv_data = list(load_dataset("ccdv/arxiv-summarization", split="train[:2000]"))
    except:
        print("ArXiv dataset not available, using C4 only")
        arxiv_data = []
    
    return c4_data + arxiv_data

# 2. 问题生成 - 完全本地化
class QuestionGenerator:
    def __init__(self):
        print("Loading language models...")
        self.generator = pipeline(
            "text-generation", 
            model="Qwen/Qwen2.5-7B",
            device_map="auto",
            torch_dtype=torch.float16,
            load_in_4bit=True
        )
        self.obfuscator = pipeline(
            "text2text-generation", 
            model="google/flan-t5-base",
            device_map="auto"
        )
    
    def generate_cross_page_qa(self, doc1, doc2):
        """Generate cross-document reasoning question"""
        prompt = f"""
        Generate a question requiring comprehensive reasoning based on two texts:
        Text 1: {doc1[:500]}...
        Text 2: {doc2[:500]}...
        
        Requirements:
        1. The question must require information from both texts
        2. The answer should not be explicitly stated in either text
        3. Output format: {{"question": "question_content", "answer": "answer"}}
        """
        result = self.generator(prompt, max_new_tokens=150)[0]['generated_text']
        return self._parse_json_output(result)
    
    def generate_riddle(self, text):
        """Generate riddle-style question"""
        # Extract entities using regex
        entities = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        if not entities: 
            return None
        
        target_entity = random.choice(entities)
        
        # Obfuscate entity
        obfuscation_prompt = f"Replace the entity with a vague description: '{target_entity}'"
        obfuscated = self.obfuscator(obfuscation_prompt, max_length=50)[0]['generated_text']
        
        # Build riddle
        context = text.replace(target_entity, "[REDACTED]", 1)
        question = f"What does '{obfuscated}' refer to in the context?"
        
        return {
            "question": question,
            "answer": target_entity,
            "context": context
        }
    
    def _parse_json_output(self, text):
        """Parse JSON from LLM output"""
        try:
            # Find first JSON-like structure
            start = text.find('{')
            end = text.rfind('}')
            if start == -1 or end == -1:
                return {"question": "Invalid format", "answer": ""}
                
            json_str = text[start:end+1]
            return json.loads(json_str)
        except json.JSONDecodeError:
            return {"question": "JSON parse error", "answer": ""}

# 3. 难度标注系统
class DifficultyTagger:
    def __init__(self):
        # 使用轻量级模型
        self.evaluator = pipeline(
            "text-classification", 
            model="distilbert-base-uncased",
            device_map="auto"
        )
    
    def tag_difficulty(self, question, answer):
        """
        Simulate pass@k difficulty tagging
        Simplified implementation for local use
        """
        complexity = self._estimate_complexity(question)
        ambiguity = self._estimate_ambiguity(question, answer)
        
        score = complexity * 0.7 + ambiguity * 0.3
        if score > 0.8: return "hard"
        if score > 0.5: return "medium"
        return "easy"
    
    def _estimate_complexity(self, text):
        """Estimate complexity based on text features"""
        words = text.split()
        if not words:
            return 0.0
            
        word_count = len(words)
        unique_ratio = len(set(words)) / word_count
        return min(0.9, (word_count/100 + unique_ratio))
    
    def _estimate_ambiguity(self, question, answer):
        """Estimate question ambiguity"""
        try:
            q_result = self.evaluator(question, truncation=True)[0]
            a_result = self.evaluator(answer, truncation=True)[0]
            return abs(q_result['score'] - a_result['score'])
        except:
            return random.uniform(0.3, 0.7)

# 4. 添加噪声模拟真实网页
def add_web_noise(text, noise_level=0.2):
    """Add noise to simulate real web content"""
    # Skip if text is too short
    if len(text) < 50:
        return text
        
    words = text.split()
    
    # Random deletion
    if random.random() < noise_level and len(words) > 10:
        del_idx = random.randint(0, len(words)-1)
        words.pop(del_idx)
    
    # Random replacement
    if random.random() < noise_level and len(words) > 5:
        rep_idx = random.randint(0, len(words)-1)
        words[rep_idx] = random.choice(["related", "important", "reportedly", "according to sources"])
    
    # Add unrelated content
    if random.random() < noise_level/3:
        ads = [
            "Sponsored content: Click for details",
            "Advertisement: Special offer today",
            "Recommended for you: Similar products"
        ]
        words.insert(random.randint(0, len(words)//2), random.choice(ads))
    
    return " ".join(words)

# 5. 数据生成主流程
def generate_dataset(output_path="webpuzzle_dataset.jsonl", num_samples=100):
    base_data = load_base_data()
    if not base_data:
        print("Error: No base data loaded")
        return
        
    generator = QuestionGenerator()
    tagger = DifficultyTagger()
    
    print(f"Generating {num_samples} samples...")
    with open(output_path, "w", encoding="utf-8") as f:
        # 添加tqdm进度条
        progress_bar = tqdm(total=num_samples, desc="Generating samples")
        
        sample_count = 0
        while sample_count < num_samples:
            # 随机选择文档
            doc1 = random.choice(base_data)
            doc2 = random.choice(base_data)
            
            # 获取文本内容
            text1 = doc1['text'] if isinstance(doc1, dict) else doc1
            text2 = doc2['text'] if isinstance(doc2, dict) else doc2
            
            # 添加噪声
            text1 = add_web_noise(text1)
            text2 = add_web_noise(text2)
            
            # 50%生成跨页问题，50%生成谜题
            if random.random() > 0.5:
                item = generator.generate_cross_page_qa(text1, text2)
                item['type'] = "cross_page"
            else:
                item = generator.generate_riddle(text1)
                if not item: 
                    continue
                item['type'] = "riddle"
            
            # 跳过生成失败的项目
            if "question" not in item or "answer" not in item:
                continue
                
            # 添加元数据
            item['id'] = f"webpuzzle_{sample_count+1}"
            item['difficulty'] = tagger.tag_difficulty(item['question'], item['answer'])
            
            # 写入文件
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
            
            sample_count += 1
            progress_bar.update(1)
        
        progress_bar.close()
    
    print(f"Dataset generated at: {output_path}")

# 运行生成
if __name__ == "__main__":
    # 生成100条样本（实际使用可增加）
    generate_dataset(num_samples=100)