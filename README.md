# OpenWebPuzzle

## 概述

OpenWebPuzzle 是一个模拟真实网页环境的问答数据集，包含 500 个需要综合推理能力的问答对。这些问题模拟了用户在浏览多个网页时需要连接不同信息片段来解决复杂问题的场景。

## 数据集详情

| 属性 | 值 |
|------|----|
| 样本数量 | 500 |
| 问题类型 | 跨页推理、谜语式问题 |
| 难度分布 | 简单(easy)、中等(medium)、困难(hard) |
| 生成模型 | Qwen3-Coder-480B-A35B (Iflow API) |
| 数据来源 | C4数据集、中文维基百科 |
| 文件格式 | JSON Lines (.jsonl) |
| 文件大小 | 1123 KB |

## 数据结构

每个样本为 JSON 对象，包含以下字段：

```json
{
  "question": "如何利用天体物理环境中产生的不稳定核素的理论预测模型，结合珍珠光泽材料的特性，设计出既符合核反应稳定性要求又具备优雅珠宝美学的新型材料？",      "answer": "通过理论模型预测核反应产生的稳定核素的物理特性（如耐久性与光学性质），将其与珍珠光泽的柔和质感及金属材料的工艺结合，可开发出兼具科学稳定性与美学价值的珠宝。需平衡核素的实验验证需求与珠宝设计的简约风格，确保材料在极端环境下的稳定性同时满足优雅外观的需求。",
  "type": "cross_page",
  "id": "webpuzzle_1",
  "difficulty": "medium"
}
```

### 字段说明

- **question**: 问题
- **answer**: 答案
- **type**: 类型，包括 cross_page 和 riddle
- **id**: 唯一个ID
- **difficulty**: 难度，由规则引擎标注

## 使用示例

### Python 加载代码

```python
import json

# 加载数据集
dataset = []
with open("webpuzzle_dataset.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        dataset.append(json.loads(line))

print(f"加载 {len(dataset)} 个样本")
print(f"第一个样本: {dataset[0]['question']}")
```

### 数据集应用场景

1. **大语言模型训练**：增强模型综合推理能力
2. **问答系统评估**：测试系统处理复杂问题的能力
3. **教育技术**：构建需要高阶思维能力的练习材料
4. **信息检索研究**：测试跨文档信息整合能力

## 生成方法

数据集通过以下流程生成：

1. **数据源准备**：
   - 英文：C4数据集（Colossal Cleaned Crawl）
   - 中文：中文维基百科
   
2. **问题生成**：
   - 使用通义千问API生成跨页推理问题和谜语式问题
   - 添加网页噪声模拟真实环境

3. **难度标注**：
   - 基于规则系统自动标注难度
   - 考虑问题长度、答案长度等特征

4. **质量控制**：
   - 自动过滤无效响应
   - 限制token使用确保质量一致性

## 使用许可

本数据集采用 MIT 许可协议：

## 联系方式

如有任何问题或建议，请联系：
- GitHub：https://github.com/MengAiDev/OpenWebPuzzle
- ModelScope: https://modelscope.cn/datasets/MengAiDev/OpenWebPuzzle
- Kaggle Notebook: https://www.kaggle.com/code/mengaidev/open-web-puzzle

## 已知限制

1. 部分问题可能受限于源文本质量
2. 难度标注为自动生成，未经人工验证
