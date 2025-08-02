import json
import os
from datetime import datetime
from openai import OpenAI
from typing import List, Dict

def get_title_from_gpt(history: List[Dict[str, str]]) -> str:
    client = OpenAI()
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "以下の会話のタイトルを20文字以内で生成してください。"},
                {"role": "user", "content": json.dumps(history, ensure_ascii=False)}
            ],
            stream=False,
        )
        title = response.choices[0].message.content
        if title:
            return "".join(c for c in title if c.isalnum() or c in (' ', '_')).rstrip()
        else:
            return "無題のチャット"
    except Exception as e:
        print(f"タイトル生成エラー: {e}")
        return "無題のチャット"

def save_chat_history(history: List[Dict[str, str]], save_dir: str = "saved_chats") -> str:
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    title_source = history[:3] if len(history) > 2 else history
    if not title_source:
        title = "空のチャット"
    else:
        title = get_title_from_gpt(title_source)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{title}.json"
    filepath = os.path.join(save_dir, filename)

    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=4)
        return f"会話を保存しました: {filepath}"
    except Exception as e:
        return f"保存に失敗しました: {e}"

def convert_history_to_markdown(history: List[Dict[str, str]]) -> str:
    """
    会話履歴をAIコーディング指示書向けのMarkdown形式に変換します。
    """
    markdown_lines = ["# AIコーディング指示書\n"]
    for message in history:
        role = "開発者" if message["role"] == "user" else "AIアシスタント"
        content = message["content"]
        markdown_lines.append(f"## ■ {role}からの入力\n")
        markdown_lines.append(f"```text\n{content}\n```\n")
    
    return "\n".join(markdown_lines)

def list_saved_chats(save_dir: str) -> List[str]:
    """指定されたディレクトリ内の保存済みチャット(JSON)のリストを返します。"""
    if not os.path.exists(save_dir):
        return []
    files = [f for f in os.listdir(save_dir) if f.endswith('.json')]
    files.sort(key=lambda f: os.path.getmtime(os.path.join(save_dir, f)), reverse=True)
    return files

def load_chat_history(filepath: str) -> List[Dict[str, str]]:
    """指定されたJSONファイルからチャット履歴を読み込みます。"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"チャット履歴の読み込みに失敗しました: {e}")
        return []