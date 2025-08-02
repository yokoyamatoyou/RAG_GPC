
import json
import os
from datetime import datetime
from openai import OpenAI

def get_title_from_gpt(history):
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
        return response.choices[0].message.content
    except Exception as e:
        print(f"タイトル生成エラー: {e}")
        return "無題のチャット"

def save_chat_history(history, save_dir="saved_chats"):
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    title = get_title_from_gpt(history[:3]) # 最初の3つのやり取りでタイトル生成
    timestamp = datetime.now().strftime("%Y%m%d")
    filename = f"{timestamp}_{title}.json"
    filepath = os.path.join(save_dir, filename)

    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=4)
        return f"会話を保存しました: {filepath}"
    except Exception as e:
        return f"保存に失敗しました: {e}"
