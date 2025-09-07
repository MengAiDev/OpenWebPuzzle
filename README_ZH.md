# OpenWebPuzzle

## 概述

OpenWebPuzzle 是一个模拟真实网络环境的问答数据集，包含 500 个需要综合推理能力的问题-答案对。这些问题模拟了用户在多个网页间连接不同信息片段以解决复杂问题的场景。

## 数据集详情

请查看：https://modelscope.cn/datasets/MengAiDev/OpenWebPuzzle

## 数据结构

每个样本是一个包含以下字段的 JSON 对象：

```json
{
  "question": "如何将天体物理环境中产生的不稳定核素的理论预测模型与珍珠光泽材料的特性相结合，设计出既满足核反应稳定性要求又具有优雅珠宝美学的新材料？",
  "answer": "通过使用理论模型预测核反应中产生的稳定核素的物理特性（如耐久性和光学特性），并将其与珍珠光泽的柔软质地和金属材料的工艺相结合，可以开发出兼具科学稳定性和美学价值的新型珠宝材料。必须平衡核素的实验验证要求与珠宝设计的简约风格，确保材料在极端环境中的稳定性，同时满足优雅外观的需求。",
  "type": "cross_page",
  "id": "webpuzzle_1",
  "difficulty": "medium"
}
```

以及

```json
{
  "question": "上下文中的'一位知名音乐制作人'指的是什么？",
  "answer": "Karat Faye",
  "context": "感谢乐队成员 Arnie、Brian 和 Dane 使这首音乐成为可能，迟来总比不到好！特别感谢 Robert Margouleff 和 [被遮挡] 在洛杉矶工作室提供的音乐专业知识。感谢他们提供了完美美丽的工作氛围，使我能够将这些录音重现生机。",
  "type": "riddle", 
  "id": "webpuzzle_10",
  "difficulty": "medium"
}
```

### 字段说明

- **question**: 问题文本
- **answer**: 答案文本  
- **type**: 问题类型，包括跨页面推理(cross_page)和谜题式(riddle)
- **id**: 唯一标识符
- **difficulty**: 难度等级，基于规则引擎标注

以及

- **context**: 上下文来源（部分样本包含）

## 使用示例

### Python 加载代码

```python
import json

# 加载数据集
dataset = []
with open("webpuzzle_dataset.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        dataset.append(json.loads(line))

print(f"已加载 {len(dataset)} 个样本")
print(f"第一个样本问题: {dataset[0]['question']}")
```

### 数据集应用场景

1. **大语言模型训练**：增强模型的综合推理能力
2. **问答系统评估**：测试系统处理复杂问题的能力
3. **教育技术**：构建需要高阶思维能力的练习材料
4. **信息检索研究**：测试跨文档信息整合能力

## 生成方法

数据集通过以下流程生成：

1. **数据源准备**：
   - 英文：C4 数据集（大规模清洁爬虫数据）
   - 中文：中文维基百科
   
2. **问题生成**：
   - 使用 Qwen API 生成跨页面推理问题和谜题式问题
   - 添加网络噪声以模拟真实环境

3. **难度标注**：
   - 基于规则系统自动标注难度等级
   - 考虑问题长度、答案长度等特征

4. **质量控制**：
   - 自动过滤无效回答
   - 限制 token 使用以确保质量一致性

## 许可协议

本数据集采用 MIT 许可协议：

## 联系我们

如有任何问题或建议，请联系：
- GitHub: https://github.com/MengAiDev/OpenWebPuzzle
- ModelScope: https://modelscope.cn/datasets/MengAiDev/OpenWebPuzzle  
- Kaggle Notebook: https://www.kaggle.com/code/mengaidev/open-web-puzzle

## 已知限制

1. 部分问题可能受限于源文本质量
2. 难度标签为自动生成，未经人工验证
