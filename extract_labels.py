import json
import os

# 定义文件路径（使用绝对路径）
file_path = os.path.join(os.path.dirname(__file__), 'contributions.json')

# 打开并读取 JSON 文件
with open(file_path, 'r', encoding='utf-8') as file:
    data = json.load(file)

# 提取所有标签
labels = set()  # 使用集合以避免重复
for command, details in data.get("commands", {}).items():
    label = details.get("label")
    if label:
        labels.add(label)

# 将所有标签写入文件
with open('labels.txt', 'w', encoding='utf-8') as output_file:
    output_file.write("请为以下标签提供翻译：\n")
    for label in labels:
        output_file.write(label + "\n")

print("标签已写入 labels.txt 文件。") 