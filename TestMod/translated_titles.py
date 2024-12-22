import json
import os

# 定义文件路径（使用绝对路径）
file_path = os.path.join(os.path.dirname(__file__), 'contributions.json')
translations_file_path = os.path.join(os.path.dirname(__file__), 'labels2_translations.json')

# 打开并读取 JSON 文件
with open(file_path, 'r', encoding='utf-8') as file:
    data = json.load(file)

# 打开并读取翻译字典文件
with open(translations_file_path, 'r', encoding='utf-8') as translations_file:
    translations = json.load(translations_file)

# 遍历 JSON 数据，获取所有配置的标题并替换
for config in data.get("contributes", {}).get("submenus", []):
    title = config.get("label")
    if title in translations:
        # 替换原标题
        config['label'] = translations[title]
        print(f'Original: {title} -> Translated: {translations[title]}')

# 将更新后的数据写回 JSON 文件
with open(file_path, 'w', encoding='utf-8') as file:
    json.dump(data, file, ensure_ascii=False, indent=4)

print("Translation and replacement completed.")