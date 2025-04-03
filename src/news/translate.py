from time import sleep
import requests
import os
import traceback

def call_openai_api(prompt):
    url = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
    api_key="d9b9ca11-7273-4b7e-a8e6-a1518a5c02b4"
    model="deepseek-v3-250324"

    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": """
             - reply in english
             - everything is for SEO
             """},
            {"role": "user", "content": prompt}
            ],
        "temperature": 0.7
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()

        return response.json()['choices'][0]['message']['content']
    except requests.exceptions.RequestException as e:
        print(f"Error calling OpenAI API: {e}")
        return None

def call_gemini_api(prompt):
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro-exp-03-25:generateContent"
    api_key = "AIzaSyCcmhi5dWdx3iOVOMsQ0_NVoBarZlrR6NQ"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    data = {
        "contents": [{
            "parts":[{
                "text": prompt
            }]
        }],
        "generationConfig": {
            "temperature": 0.7
        }
    }
    
    try:
        response = requests.post(
            f"{url}?key={api_key}",
            headers=headers, 
            json=data
        )
        response.raise_for_status()
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    except requests.exceptions.RequestException as e:
        print(f"Error calling Gemini API: {e}")
        return None
    


# 你预先定义的 AI 翻译函数
def callai(prompt,language):
    # 示例：请替换为你实际的 AI 调用逻辑
    prompt= f"""
你是我Astro博客的翻译机器,你需要将我的mdx文件翻译成多国语言,现在将以下内容翻译成 {language} 语言,切记,只回复翻译结果,任何多余的内容都会导致程序出错,请务必只返回结果:
```
{prompt}
```
"""
    return call_openai_api(prompt)

# 支持的语言文件夹
LANGUAGES = ['es', 'fr', 'de', 'ja', 'en', 'ru', 'pt', 'ar', 'ko']

# 获取当前目录所有 .mdx 文件
def get_mdx_files():
    return [f for f in os.listdir('.') if f.endswith('.mdx') and os.path.isfile(f)]

# 确保语言文件夹存在
def ensure_language_dirs():
    for lang in LANGUAGES:
        os.makedirs(lang, exist_ok=True)

# 读取 .mdx 文件内容
def read_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"[错误] 读取文件失败: {filepath}\n{e}")
        return None

# 写入翻译后的内容到对应语言目录
def write_translated_file(lang, filename, content):
    try:
        output_path = os.path.join(lang, filename)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"[成功] 写入翻译文件: {output_path}")
    except Exception as e:
        print(f"[错误] 写入文件失败: {output_path}\n{e}")

# 主流程
def translate_mdx_files():
    ensure_language_dirs()
    mdx_files = get_mdx_files()

    if not mdx_files:
        print("没有找到任何 .mdx 文件。")
        return

    for mdx_file in mdx_files:
        print(f"\n处理文件: {mdx_file}")
        content = read_file(mdx_file)
        if content is None:
            continue  # 跳过错误文件

        for lang in LANGUAGES:
            try:
                prompt = content
                translated = callai(prompt, lang)
                translated = translated.replace('```mdx', '').replace('```', '')
                write_translated_file(lang, mdx_file, translated)
                sleep(5)  # 避免调用频率过快
            except Exception as e:
                print(f"[错误] 语言 {lang} 的翻译失败: {mdx_file}\n{traceback.format_exc()}")

if __name__ == "__main__":
    translate_mdx_files()
