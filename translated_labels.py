import json
import os

# 定义文件路径（使用绝对路径）
file_path = os.path.join(os.path.dirname(__file__), 'contributions.json')
translations_file_path = os.path.join(os.path.dirname(__file__), 'translations.json')

# 打开并读取 JSON 文件
with open(file_path, 'r', encoding='utf-8') as file:
    data = json.load(file)

# 打开并读取翻译字典文件
with open(translations_file_path, 'r', encoding='utf-8') as translations_file:
    translations = json.load(translations_file)

# 遍历 JSON 数据，获取所有命令的标签并替换 submenus label
# for command, details in data.get("commands", {}).items(): 
for command, details in data.get("contributes", {}).get("submenus", []):
    label = details.get("label")
    if label in translations:
        # 替换原标签
        details['label'] = translations[label]
        print(f'Original: {label} -> Translated: {translations[label]}')

# 将更新后的数据写回 JSON 文件
with open(file_path, 'w', encoding='utf-8') as file:
    json.dump(data, file, ensure_ascii=False, indent=4)

print("Translation and replacement completed.")