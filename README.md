# OpenWebPuzzle

## Overview

OpenWebPuzzle is a question-answering dataset that simulates real web environments, containing 7k question-answer pairs requiring comprehensive reasoning skills. These questions mimic scenarios where users need to connect different pieces of information across multiple web pages to solve complex problems.

## Dataset Details

Please see at: https://modelscope.cn/datasets/MengAiDev/OpenWebPuzzle

## Data Structure

Each sample is a JSON object containing the following fields:

```json
{
  "question": "How can theoretical prediction models of unstable nuclides produced in astrophysical environments be combined with the characteristics of pearl luster materials to design new materials that meet both nuclear reaction stability requirements and possess elegant jewelry aesthetics?",      "answer": "By using theoretical models to predict the physical properties (such as durability and optical characteristics) of stable nuclides produced in nuclear reactions, and integrating them with the soft texture of pearl luster and the craftsmanship of metal materials, new jewelry materials that combine scientific stability and aesthetic value can be developed. It is essential to balance the experimental validation requirements of nuclides with the minimalist style of jewelry design, ensuring the material's stability in extreme environments while meeting the demands of an elegant appearance.",
  "type": "cross_page",
  "id": "webpuzzle_1",
  "difficulty": "medium"
}
```

And

```json
{
  "question": "上下文中的'一位知名音乐制作人'指的是什么？",
  "answer": "Karat Faye",
  "context": "Thanks to the band, Arnie, Brian, and Dane for making this music possible, better late than never! Special thanks to Robert Margouleff and [REDACTED] for their musical expertise in the L.A. Studios. For providing a perfectly beautiful working atmosphere so that I could bring these recordings back to life.",
  "type": "riddle",
  "id": "webpuzzle_10",
  "difficulty": "medium"
}
```
### Field Descriptions

- **question**: The question
- **answer**: The answer
- **type**: Type, including cross_page and riddle
- **id**: Unique ID
- **difficulty**: Difficulty, labeled by a rule-based engine

And

- **content**: The source

## Usage Example

### Python Loading Code

```python
import json

# Load the dataset
dataset = []
with open("webpuzzle_dataset.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        dataset.append(json.loads(line))

print(f"Loaded {len(dataset)} samples")
print(f"First sample: {dataset[0]['question']}")
```

### Dataset Application Scenarios

1. **Large Language Model Training**: Enhances the model's comprehensive reasoning capabilities.
2. **Question-Answering System Evaluation**: Tests the system's ability to handle complex problems.
3. **Educational Technology**: Constructs exercise materials requiring higher-order thinking skills.
4. **Information Retrieval Research**: Tests cross-document information integration capabilities.

## Generation Method

The dataset was generated through the following process:

1. **Data Source Preparation**:
   - English: C4 Dataset (Colossal Cleaned Crawl)
   - Chinese: Chinese Wikipedia
   
2. **Question Generation**:
   - Used the Qwen API to generate cross-page reasoning questions and riddle-style questions.
   - Added web noise to simulate real environments.

3. **Difficulty Labeling**:
   - Automatically labeled difficulty based on a rule-based system.
   - Considered features such as question length and answer length.

4. **Quality Control**:
   - Automatically filtered invalid responses.
   - Limited token usage to ensure consistent quality.

## License

This dataset is licensed under the MIT License:

## Contact

For any questions or suggestions, please contact:
- GitHub: https://github.com/MengAiDev/OpenWebPuzzle
- ModelScope: https://modelscope.cn/datasets/MengAiDev/OpenWebPuzzle
- Kaggle Notebook: https://www.kaggle.com/code/mengaidev/open-web-puzzle

## Known Limitations

1. Some questions may be limited by the quality of the source text.
2. Difficulty labels are automatically generated and have not been manually verified.
