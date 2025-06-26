import json
import random
import re
import time
import requests
from datasets import load_dataset
from tqdm.auto import tqdm

# 设置随机种子保证可复现
random.seed(42)

# 智谱AI API配置 - 替换为你的实际API密钥
API_KEY = "your_api_key_here"  # 从智谱AI平台获取
API_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
MODEL_NAME = "glm-4"  # 使用GLM-4模型

def call_chatglm_api(prompt, max_tokens=512, temperature=0.7):
    """调用智谱AI的API生成文本"""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": temperature
    }
    
    try:
        response = requests.post(API_URL, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        result = response.json()
        return result['choices'][0]['message']['content']
    except Exception as e:
        print(f"API调用失败: {str(e)}")
        return ""

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

# 2. 问题生成 - 使用云端API
class QuestionGenerator:
    def generate_cross_page_qa(self, doc1, doc2):
        """Generate cross-document reasoning question using API"""
        prompt = f"""
        请基于以下两个文本生成一个需要综合推理的问题：
        
        文本1: {doc1[:500]}...
        文本2: {doc2[:500]}...
        
        要求：
        1. 问题必须同时需要两个文本的信息
        2. 答案不能直接在任一文本中明确写出
        3. 输出格式必须是严格的JSON格式：{{"question": "问题内容", "answer": "答案"}}
        """
        
        result = call_chatglm_api(prompt)
        return self._parse_json_output(result)
    
    def generate_riddle(self, text):
        """Generate riddle-style question"""
        # 使用正则表达式提取实体
        entities = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        if not entities: 
            return None
        
        target_entity = random.choice(entities)
        
        # 使用API混淆实体
        prompt = f"请将以下实体替换为模糊的描述：'{target_entity}'。只需输出替换后的描述文本，不要包含其他内容。"
        obfuscated = call_chatglm_api(prompt, max_tokens=50)
        
        # 构建谜题
        context = text.replace(target_entity, "[REDACTED]", 1)
        question = f"上下文中的'{obfuscated}'指的是什么？"
        
        return {
            "question": question,
            "answer": target_entity,
            "context": context
        }
    
    def _parse_json_output(self, text):
        """Parse JSON from API output"""
        try:
            # 尝试提取JSON部分
            start = text.find('{')
            end = text.rfind('}')
            if start == -1 or end == -1:
                return {"question": "无效格式", "answer": ""}
                
            json_str = text[start:end+1]
            return json.loads(json_str)
        except json.JSONDecodeError:
            return {"question": "JSON解析错误", "answer": ""}

# 3. 难度标注系统 - 使用规则方法
class DifficultyTagger:
    def tag_difficulty(self, question, answer):
        """
        基于规则标注难度
        """
        complexity = self._estimate_complexity(question)
        ambiguity = self._estimate_ambiguity(question, answer)
        
        score = complexity * 0.7 + ambiguity * 0.3
        if score > 0.8: return "hard"
        if score > 0.5: return "medium"
        return "easy"
    
    def _estimate_complexity(self, text):
        """基于文本特征估计复杂度"""
        words = text.split()
        if not words:
            return 0.0
            
        word_count = len(words)
        unique_ratio = len(set(words)) / word_count
        return min(0.9, (word_count/100 + unique_ratio))
    
    def _estimate_ambiguity(self, question, answer):
        """估计问题的模糊性（简化实现）"""
        # 基于问题长度和答案长度的差异
        q_len = len(question)
        a_len = len(answer)
        return min(0.9, abs(q_len - a_len) / max(q_len, a_len))

# 4. 添加噪声模拟真实网页
def add_web_noise(text, noise_level=0.2):
    """Add noise to simulate real web content"""
    # 文本过短时跳过
    if len(text) < 50:
        return text
        
    words = text.split()
    
    # 随机删除
    if random.random() < noise_level and len(words) > 10:
        del_idx = random.randint(0, len(words)-1)
        words.pop(del_idx)
    
    # 随机替换
    if random.random() < noise_level and len(words) > 5:
        rep_idx = random.randint(0, len(words)-1)
        words[rep_idx] = random.choice(["相关", "重要", "据报道", "根据消息来源"])
    
    # 添加不相关内容
    if random.random() < noise_level/3:
        ads = [
            "赞助内容：点击查看详情",
            "广告：今日特惠",
            "为您推荐：类似产品"
        ]
        words.insert(random.randint(0, len(words)//2), random.choice(ads))
    
    return " ".join(words)

# 5. 数据生成主流程
def generate_dataset(output_path="webpuzzle_dataset.jsonl", num_samples=100):
    base_data = load_base_data()
    if not base_data:
        print("错误：未加载基础数据")
        return
        
    generator = QuestionGenerator()
    tagger = DifficultyTagger()
    
    print(f"生成 {num_samples} 个样本...")
    with open(output_path, "w", encoding="utf-8") as f:
        # 添加进度条
        progress_bar = tqdm(total=num_samples, desc="生成样本")
        
        sample_count = 0
        while sample_count < num_samples:
            # 随机选择文档
            doc1 = random.choice(base_data)
            doc2 = random.choice(base_data)
            
            # 获取文本内容
            text1 = doc1[list(doc1.keys())[0]]
            text2 = doc2[list(doc2.keys())[0]]
            
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
            
            # 添加延迟以避免API速率限制
            time.sleep(1.5)
        
        progress_bar.close()
    
    print(f"数据集已生成: {output_path}")

# 运行生成
if __name__ == "__main__":
    # 生成样本（建议从较小数量开始）
    generate_dataset(num_samples=50)  # 开始时使用较小的数量
